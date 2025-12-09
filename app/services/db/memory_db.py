from sqlalchemy.orm import Session

from datetime import timedelta, datetime, timezone, date
from typing import Optional, List
from app.models.memory_item import MemoryItem
from ..memory_manager import SHORT_TERM_THRESHOLD

# 负责执行与记忆有关db操作逻辑
class MemoryDB:
    # 需要一个db会话来执行存取逻辑
    def __init__(self, db: Session):
        self.db = db

    def add_memory_item(
        self,
        user_id: int,
        *,
        mem_type: str,
        summary: str,
        embedding: List[float],
        importance: int = 0,
        date_value: Optional[date] = None,
        source_type: Optional[str] = None,
        source_id: Optional[int] = None,
        base_weight: Optional[float] = None,
    ) -> MemoryItem:
        if base_weight is None:
            base_weight = {0: 0.8, 1: 1.2, 2: 1.6}.get(importance, 1.0)

        item = MemoryItem(
            user_id=user_id,
            type=mem_type,
            date=date_value,
            summary=summary,
            embedding=embedding,
            source_type=source_type,
            source_id=source_id,
            weight=base_weight,
            importance=importance,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def load_candidate_memories(
        self,
        user_id: int,
        scene: str,
    ) -> List[MemoryItem]:
        """
        DB 层：根据场景选出记忆候选集。
        这里只负责“类型过滤 + 短期阈值”，不算相似度。
        """
        q = self.db.query(MemoryItem).filter(MemoryItem.user_id == user_id)
        types = ["short_term", "long_term"]

        q = q.filter(MemoryItem.type.in_(types))

        # 短期记忆必须权重>=阈值才算“活跃”
        # 长期记忆不受此限制
        items = q.all()
        candidates: List[MemoryItem] = []
        for item in items:
            if item.type == "short_term" and item.weight < SHORT_TERM_THRESHOLD:
                continue
            candidates.append(item)

        return candidates
