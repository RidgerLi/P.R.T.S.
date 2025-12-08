from sqlalchemy.orm import Session

from .db.conversation_db import ConversationRepository
from .promt_builder import build_conversation_prompt
from .ai_client import chat

class NomalConversationScene:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ConversationRepository(db)

    def chat(self, user_id: int, user_input: str) -> tuple[str, int]: # 返回reply文字和session.id
        # 查询近期session
        session = self.repo.get_or_create_active_conversation_session(user_id=user_id)

        # 查询近期对话列表
        session_messages = self.repo.get_recent_messages_in_session(session)

        # 构建prompt
        prompt = build_conversation_prompt(session_messages=session_messages, user_input=user_input)

        # 执行对话
        reply = chat(prompt)

        # 把自己的话放入库中
        self.repo.add_message("user", user_input, session)
        # 把对方的回复加入到库中
        self.repo.add_message("assistant", reply, session)

        return [reply, session.id]


