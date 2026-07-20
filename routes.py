from fastapi import Depends, HTTPException, status
from fastapi import APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import models
import schemas
from crud import hash_password,verify_password,create_access_token,get_current_user,make_reset_code
from database import  get_db
router = APIRouter()
@router.post("/signup", response_model=schemas.TokenResponse)
def signup(body: schemas.SignupRequest, db: Session = Depends(get_db)):
    email = body.email.lower()
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(400, "An account with this email already exists.")

    user = models.User(
        name=body.name,
        email=email,
        phone=body.phone or "",
        address="",
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(email)
    return schemas.TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    email = body.email.lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Email or password is incorrect.")

    token = create_access_token(email)
    return schemas.TokenResponse(access_token=token, user=user)


@router.get("/profile", response_model=schemas.UserOut)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=schemas.UserOut)
def update_profile(
        body: schemas.ProfileUpdate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    updates = body.model_dump(exclude_none=True)
    for key, value in updates.items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/booking", status_code=status.HTTP_201_CREATED, response_model=schemas.BookingOut)
def create_booking(
        body: schemas.BookingCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    order = models.BookOrder(
        user_id=current_user.id,
        service=body.service,
        date=body.date,
        window=body.window,
        address=body.address,
        note=body.note,
        status="Scheduled",

    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/bookings", response_model=list[schemas.BookingOut])
def list_bookings(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return (
        db.query(models.BookOrder)
        .filter(models.BookOrder.user_id == current_user.id)
        .order_by(models.BookOrder.created_at.desc())
        .all()
    )


@router.post("/booking/{booking_id}/cancel", response_model=schemas.BookingOut)
def cancel_booking(
        booking_id: int,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    order = (
        db.query(models.BookOrder)
        .filter(
            models.BookOrder.id == booking_id,
            models.BookOrder.user_id == current_user.id,
        )
        .first()
    )
    if not order:
        raise HTTPException(404, "Booking not found.")

    order.status = "Cancelled"
    db.commit()
    db.refresh(order)
    return order


@router.post("/forgot-password")
def forgot_password(body: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = body.email.lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(404, "No account found for that email.")

    code = make_reset_code()

    existing = (
        db.query(models.PasswordResetCode)
        .filter(models.PasswordResetCode.email == email)
        .first()
    )
    if existing:
        existing.code = code
        existing.created_at = datetime.now(timezone.utc)
    else:
        db.add(models.PasswordResetCode(email=email, user_id=user.id, code=code))
    db.commit()

    return {"message": "Reset code generated.", "code": code}


@router.post("/reset-password")
def reset_password(body: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    email = body.email.lower()
    reset_entry = (
        db.query(models.PasswordResetCode)
        .filter(models.PasswordResetCode.email == email)
        .first()
    )
    if not reset_entry or reset_entry.code != body.code.upper():
        raise HTTPException(400, "That reset code doesn't match.")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(404, "No account found for that email.")

    user.password_hash = hash_password(body.new_password)
    db.delete(reset_entry)
    db.commit()
    return {"message": "Password updated."}