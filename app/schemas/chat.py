from pydantic import BaseModel
from typing import Optional
from datetime import date

class EchoRequest(BaseModel):
    message: str

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = 1

class ChatResponse(BaseModel):
    reply: str
    session_id: int

class MemoryItemDTO(BaseModel):
    id: int
    type: str
    summary: str
    date: Optional[date]