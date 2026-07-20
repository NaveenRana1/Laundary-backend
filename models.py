from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, default="")
    address = Column(String, default="")
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    orders = relationship(
        "BookOrder", back_populates="user", cascade="all, delete-orphan"
    )
    reset_codes = relationship(
        "PasswordResetCode", back_populates="user", cascade="all, delete-orphan"
    )


class BookOrder(Base):
    __tablename__ = "book_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    service = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    # "window" is a reserved word in Postgres; SQLAlchemy auto-quotes it
    # because the column name matches a reserved identifier.
    window = Column(String, nullable=False)
    address = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    status = Column(String, default="Scheduled", nullable=False)

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    # Populated automatically on insert AND on every update - never send
    # this from the request body, and never pass None explicitly.
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    user = relationship("User", back_populates="orders")


class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    email = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="reset_codes")