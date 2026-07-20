
from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from database import engine, Base




app = FastAPI(title="FreshFold API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def health():
    return {"status": "ok", "service": "FreshFold-api"}