from sqlalchemy.orm import Session

from .db.conversation_db import ConversationDB

from app.models.chat import ChatMessage, ConversationSession

from typing import List
import logging 
logger = logging.getLogger(__name__)

class SessionManager:
    session: ConversationSession

    def __init__(self, db: Session):
        self.db = db
        self.repo = ConversationDB(db)

    def get_session_messages(self, user_id) -> List[ChatMessage]: 
        self.session = self.repo.get_or_create_active_conversation_session(user_id=user_id)
        logger.info(f"【最近会话信息】:{self.session}")
        # 查询近期对话列表
        session_messages = self.repo.get_recent_messages_in_session(self.session)
        logger.info(f"【最近会话列表】:{session_messages}")
        return session_messages
    
    def add_messages(self, user_input=str, ai_reply=str):
        # 把自己的话放入库中
        self.repo.add_message("user", user_input, self.session)
        # 把对方的回复加入到库中
        self.repo.add_message("assistant", ai_reply, self.session)