from fastapi import FastAPI
from app.routers import chat

from app.database import Base, engine
import app.models

import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)

app = FastAPI()
app.include_router(chat.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message" : "Hello from my backend!!!"}

@app.get("/ping")
def ping():
    return {"status": "oodk"}