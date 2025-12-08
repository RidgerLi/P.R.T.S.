from pydantic import BaseModel
from typing import Optional

class EchoRequest(BaseModel):
    message: str

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = 1

class ChatResponse(BaseModel):
    reply: str
    session_id: int
