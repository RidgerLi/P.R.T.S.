from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session

from app.schemas.chat import EchoRequest, ChatRequest, ChatResponse
from app.services.ai_client import echo_ai, chat_ai_test
from app.services.chat_scene import NomalConversationScene
from app.database import get_db

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/echo")
def echo(req: EchoRequest):
    response = echo_ai(req.message)

    return {"reply": response}

@router.post("/chat_test")
def chat_test(req: ChatRequest):
    response = chat_ai_test(req.messgae, req.user_id)

    return {"reply": response}

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    normal_conversation = NomalConversationScene(db)
    reply, session_id = normal_conversation.chat(
        user_id=req.user_id or 1,
        user_input=req.message,
    )
    return ChatResponse(reply=reply, session_id=session_id)

@router.post("/audio_chat", response_class=StreamingResponse)
async def audio_chat(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    user_id: int = Form(1),
    conversation_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        logger.info("收到audio chat请求")
        if not audio.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="请上传音频文件")

        audio_bytes = await audio.read()
        normal_conversation_scene = NomalConversationScene(db)
        user_input, ai_text, ai_speech_bytes, session_id = normal_conversation_scene.audio_chat(user_id=user_id, audio_bytes=audio_bytes, background_tasks=background_tasks)

        if not ai_speech_bytes:
            raise HTTPException(status_code=500, detail="TTS returned empty audio")

        # 清洗一下要放进 Header 的文本，防止换行和 None
        def sanitize_header_value(text: str | None, max_len: int = 200) -> str:
            if not text:
                return ""
            s = text[:max_len]
            # HTTP 头不能有换行符，把它们换成空格
            s = s.replace("\r", " ").replace("\n", " ")
            return s

        safe_user_text = sanitize_header_value(user_input)
        safe_reply_text = sanitize_header_value(ai_text)

        # 5. 返回 mp3 音频（如果是 wav 就改成 audio/wav）
        return Response(
            content=ai_speech_bytes,
            media_type="audio/mpeg",
            # headers={
            #     "X-User-Text": safe_user_text,
            #     "X-Reply-Text": safe_reply_text,
            #     # 你也可以顺便把 session_id 带回去，必要时前端用
            #     "X-Session-Id": str(session_id),
            # },
        )
    except HTTPException as e:
        import traceback
        logger.error("**************")
        # 打印详细信息 + traceback
        logger.error("HTTPException in /ai/audio_chat: status=%s, detail=%s", e.status_code, e.detail)
        logger.error("Stacktrace:\n%s", traceback.format_exc())
        raise  # 交给 FastAPI 去返回对应的状态码和 detail
    except Exception as e:
        import traceback
        print("==== /ai/audio_chat INTERNAL ERROR ====")
        traceback.print_exc()
        print("==== END ERROR ====")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")