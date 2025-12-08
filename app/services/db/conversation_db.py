from sqlalchemy.orm import Session

from datetime import timedelta, datetime, timezone

from app.models.chat import ChatMessage, ConversationSession

SESSION_TIMEOUT_MINUTES = 5
RECENT_MESSAGE_COUNT = 10

# 负责执行与近期对话有关db操作逻辑
class ConversationRepository:
    # 需要一个db会话来执行存取逻辑
    def __init__(self, db: Session):
        self.db = db

    # 当对话开始时，尝试找一个最近的会话记录，如果没有则创建一个返回
    # 期待更复杂的最近对话判断逻辑
    def get_or_create_active_conversation_session(self, user_id: int) -> ConversationSession:
        # 尝试找最近的一个active的session
        recent_session = (
            self.db.query(ConversationSession)
            .filter(
                ConversationSession.user_id == user_id,
                ConversationSession.status == "active",
            )
            .order_by(ConversationSession.last_activity_at.desc()) # 按照这一列降序排列
            .first()
        )

        current_time = datetime.utcnow()
        timeout = current_time - timedelta(minutes=SESSION_TIMEOUT_MINUTES)

        if recent_session is None or recent_session.last_activity_at < timeout:
            recent_session = ConversationSession(user_id=user_id)
            self.db.add(recent_session)
            self.db.commit()
            self.db.refresh(recent_session) # 由于字段需要触发器和自增id，所以需要重新同步回session

        return recent_session
    
    def add_message(self, role: str, content: str, conversation_session: ConversationSession) -> ChatMessage :
        msg = ChatMessage(role=role, content=content, session_id=conversation_session.id)
        self.db.add(msg)
        conversation_session.last_activity_at = datetime.now(timezone.utc) # 当这个对象脏了，再执行commit的时候，orm会自动update这条内容

        self.db.commit()
        self.db.refresh(msg)

        return msg
    
    def get_recent_messages_in_session(self, conversation_session: ConversationSession, limit: int = RECENT_MESSAGE_COUNT) -> List[ChatMessage] :
        db = self.db

        q = (
            db.query(ChatMessage)
                .filter(
                    ChatMessage.session_id == conversation_session.id
                )
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
        )

        messages = list(reversed(q.all())) # 让消息按照时间升序排列，早先发生的在前

        return messages