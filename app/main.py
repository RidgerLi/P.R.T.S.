from fastapi import FastAPI
from app.routers import chat

from app.database import Base, engine
import app.models

app = FastAPI()
app.include_router(chat.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message" : "Hello from my backend!!!"}

@app.get("/ping")
def ping():
    return {"status": "oodk"}