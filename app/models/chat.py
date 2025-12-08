from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, default=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship(  # 定义一对多级联关系，当conversation被删除时，对应的message也会被删除
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), index=True)
    role = Column(String(20), index = True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship( # 定义级联关系另一端
        "ConversationSession",
        back_populates="messages"
    )

