# app/models.py 里追加（不要重复定义已有表）

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Text,
    JSON,
    Float,
)
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base


class MemoryItem(Base):
    """
    统一记忆条目：
    - summary：1~3 句浓缩后的内容（给 LLM 看）
    - type：   "short_term" / "long_term"
    - embedding：summary 的向量（用于相似度检索）
    - weight：短期记忆权重，用来维护 ShortTermBuffer（>= 阈值 才算短期活跃）
    """
    __tablename__ = "memory_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, default=1)

    # "short_term" / "long_term"
    type = Column(String, nullable=False, index=True)

    # 这条记忆对应的“主要日期”（某天的事件 / 某个阶段的代表日）
    date = Column(Date, nullable=True, index=True)

    summary = Column(Text, nullable=False)

    # 向量用 JSON 存：[0.01, -0.03, ...]
    embedding = Column(JSON, nullable=False)

    # 来源追踪（可选）：比如来自哪条 chat/哪条 note
    source_type = Column(String, nullable=True)   # "chat", "note", "manual", ...
    source_id = Column(Integer, nullable=True)

    # 权重 & 重要性（决定是否留在“短期 buffer”）
    weight = Column(Float, nullable=False, default=1.0)
    importance = Column(Integer, nullable=False, default=0)  # 0/1/2

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
