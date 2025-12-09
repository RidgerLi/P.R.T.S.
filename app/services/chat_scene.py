from sqlalchemy.orm import Session

from .session_manager import SessionManager
from .memory_manager import MemoryManager
from .promt_builder import build_conversation_prompt
from .ai_client import chat

class NomalConversationScene:
    def __init__(self, db: Session):
        self.db = db

    def chat(self, user_id: int, user_input: str) -> tuple[str, int]: # 返回reply文字和session.id
        # todo 有待实现，权重衰减
        memory_manager = MemoryManager(self.db)
        memory_manager.decay_memory_weights(user_id)

        # todo 取得embedding相关记忆
        # a. 根据text获得embedding
        # b. 检索相关记忆，并返回top-K
        memories = memory_manager.retrieve_relevant_memories(user_id=user_id, user_input=user_input)

        # 查看最近session的对话列表，如果没有就添加一个session
        session_manager = SessionManager(self.db)
        session_messages = session_manager.get_session_messages(user_id)

        # 根据记忆、近期对话、用户输入构建prompt
        prompt = build_conversation_prompt(scene="chat", session_messages=session_messages, memory=memories, user_input=user_input)

        # 执行对话
        reply = chat(prompt)

        # 把原生对话内容加入库中
        session_manager.add_messages(user_input, reply)

        # 构成记忆，记忆入库
        memory_manager.learn_from_chat_turn(user_id, user_input=user_input, ai_reply=reply)

        return [reply, session_manager.session.id]


