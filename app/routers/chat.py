from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.schemas.chat import EchoRequest, ChatRequest, ChatResponse
from app.services.ai_client import echo_ai, chat_ai_test
from app.services.chat_scene import NomalConversationScene
from app.database import get_db


router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/echo")
def echo(req: EchoRequest):
    response = echo_ai(req.message)

    return {"reply": response}

@router.post("/chat_test")
def chat_test(req: ChatRequest):
    response = chat_ai_test(req.messgae, req.user_id)

    return {"reply": response}

@router.post("/chat_short_memory", response_model=ChatResponse)
def chat_short_memory(req: ChatRequest, db: Session = Depends(get_db)):
    normal_conversation = NomalConversationScene(db)
    reply, session_id = normal_conversation.chat(
        user_id=req.user_id or 1,
        user_input=req.message,
    )
    return ChatResponse(reply=reply, session_id=session_id)
