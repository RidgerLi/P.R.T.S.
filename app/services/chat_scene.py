from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks

from .session_manager import SessionManager
from .memory_manager import MemoryManager
from .promt_builder import build_conversation_prompt
from .ai_client import chat
from .audio_text_manager import run_stt, run_tts, run_stt_local
import time
import logging
logger = logging.getLogger(__name__)

class NomalConversationScene:
    start: float
    def __init__(self, db: Session):
        self.db = db

    def chat(self, user_id: int, user_input: str, background_tasks: BackgroundTasks) -> tuple[str, int]: # 返回reply文字和session.id
        # todo 有待实现，权重衰减
        memory_manager = MemoryManager(self.db)
        memory_manager.decay_memory_weights(user_id)

        # todo 取得embedding相关记忆
        # a. 根据text获得embedding
        # b. 检索相关记忆，并返回top-K
        memories = memory_manager.retrieve_relevant_memories(user_id=user_id, user_input=user_input)
        
        logger.info(f"【[TIMER] EMBED 完成，用时 {time.perf_counter() - self.start:.3f} 秒】")

        # 查看最近session的对话列表，如果没有就添加一个session
        session_manager = SessionManager(self.db)
        session_messages = session_manager.get_session_messages(user_id)

        # 根据记忆、近期对话、用户输入构建prompt
        prompt = build_conversation_prompt(scene="chat", session_messages=session_messages, memory=memories, user_input=user_input)

        # 执行对话
        reply = chat(prompt)

        def save_memory():
            # 把原生对话内容加入库中
            session_manager.add_messages(user_input, reply)

            # 构成记忆，记忆入库
            memory_manager.learn_from_chat_turn(user_id, user_input=user_input, ai_reply=reply)
            
            logger.info(f"【[TIMER] MEMORY 完成，用时 {time.perf_counter() - self.start:.3f} 秒】")

        background_tasks.add_task(save_memory)

        return [reply, session_manager.session.id]

    def audio_chat(self, user_id: int, audio_bytes: bytes, background_tasks: BackgroundTasks) -> tuple[str, str, bytes, int]: # 返回user文字, reply文字、audio byts、session.i
        self.start = time.perf_counter()
        try:
            # user_text = run_stt(audio_bytes)
            user_text = run_stt_local(audio_bytes)
            logger.info(f"【[TIMER] STT 完成，用时 {time.perf_counter() - self.start:.3f} 秒】")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"STT 失败: {e}")
        
        ai_text, session_id = self.chat(user_id=user_id, user_input=user_text, background_tasks=background_tasks)

        logger.info(f"【[TIMER] CHAT 完成，用时 {time.perf_counter() - self.start:.3f} 秒】")
        try:
            # ai_speech = run_tts(ai_text)
            ai_speech = run_tts(ai_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS 失败: {e}")
        
        logger.info(f"【[TIMER] TTS 完成，用时 {time.perf_counter() - self.start:.3f} 秒】")
        return [user_text, ai_text, ai_speech, session_id]
