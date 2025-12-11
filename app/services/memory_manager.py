from sqlalchemy.orm import Session

from typing import Optional, List
from datetime import date, datetime
import json

from .promt_builder import build_extract_memory_promt
from .ai_client import chat, embed
from .utils.utils import cosine_similarity
from ..models.memory_item import MemoryItem
from app.schemas.chat import MemoryItemDTO
from app.services.utils.embed_local import embed_text_local
import logging 
logger = logging.getLogger(__name__)

# 短期记忆权重阈值：低于这个认为“淡出短期记忆”
SHORT_TERM_THRESHOLD = 0.5
# 最多带有几个记忆
MAX_MEMORIES_PER_CALL = 128
from .db.memory_db import MemoryDB

class MemoryManager:
    def __init__(self, db: Session):
        self.db = db

    def _extract_memory_from_chat(self, user_input:str, ai_reply:str):
        # 构建抽取记忆prompt，执行chat，获得答复并解析
        message = build_extract_memory_promt(user_input, ai_reply)
        memory_reply = chat(message)

        try:
            start = memory_reply.find("{")
            end = memory_reply.rfind("}")
            if start == -1 or end == -1:
                return None
            obj = json.loads(memory_reply[start:end + 1])
            if not isinstance(obj, dict):
                return None
            return obj
        except Exception:
            return None
        
    def learn_from_chat_turn(
        self,
        user_id: int,
        *,
        user_input: str,
        ai_reply: str,
        scene: str = "chat",
    ) -> None:
        # 场景层在一轮对话结束后调用：
        # 使用 LLM 抽取一条记忆
        # 对 summary 做 embedding
        # 存入 MemoryItem（短期/长期），带初始权重
        logger.info(f"【制作记忆】")
        mem_info = self._extract_memory_from_chat(user_input, ai_reply)
        logger.info(f"【记忆内容】\n{mem_info}")
        if (not mem_info or not mem_info.get("should_remember") or 
            not mem_info.get("summary") or not mem_info.get("importance") or not mem_info.get("kind")):
            return

        importance = int(mem_info.get("importance", 0))
        summary = mem_info.get("summary")
        kind = mem_info.get("kind") or "short_term"

        # 只允许 short_term / long_term 两种类型
        mem_type = "long_term" if kind == "long_term" else "short_term"

        embedding = embed([summary])[0]

        memory_db = MemoryDB(self.db)
        memory_db.add_memory_item(
            user_id,
            mem_type=mem_type,
            summary=summary,
            embedding=embedding,
            importance=importance,
            date_value=date.today(),
            source_type="chat",
            source_id=None,  # 由于一条记忆可能由一轮/多条id构成，所以先不填写这个内容
        )

    def retrieve_relevant_memories(
        self,
        user_id: int,
        *,
        user_input: str,
        scene: str = "chat",
        limit: int = MAX_MEMORIES_PER_CALL,
    ) -> List[MemoryItemDTO]:
        """
        场景层在构建 prompt 前调用：
        - 用 embedding + cosine 从短期/长期记忆中取出若干相关条目
        - 并提升它们权重（被使用一次 = 记忆被“强化”一次）
        """
        if not user_input or user_input.__len__ == 0:
            return []
        query_emb = embed_text_local(user_input) # 此处拿用户原文进行embedding，跟记忆summary的embedding进行匹配
        memory_db = MemoryDB(self.db)
        candidates = memory_db.load_candidate_memories(user_id=user_id, scene=scene)
        if not candidates:
            return []

        scored: List[tuple[MemoryItem, float]] = []
        for item in candidates:
            try:
                emb = item.embedding or []
                sim = cosine_similarity(query_emb, emb)
                scored.append((item, sim))
            except Exception:
                continue

        # 相似度为 0 的可以先丢掉
        scored = [s for s in scored if s[1] > 0.0]
        if not scored:
            return []

        # 按相似度从高到低排序
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:limit]

        # 更新这些记忆的 weight / last_used_at
        now = datetime.utcnow()
        for item, sim in top:
            # 用一个简单规则：相似度越高，加得越多
            item.weight += 0.2 + 0.3 * sim # 初始化权重的位置
            item.last_used_at = now
        self.db.commit()

        return [
            MemoryItemDTO(
                id=item.id,
                type=item.type,
                date=item.date,
                summary=item.summary,
            )
            for item, _ in top
        ]

    def decay_memory_weights(
        self,
        user_id: int,
        *,
        now: Optional[datetime] = None,
    ) -> None:
        """
        记忆权重衰减 & 清理接口（暂时不实现逻辑）。
        之后可以：
        - 根据时间（距离 now 多久）衰减 weight
        - 检测“睡眠段”后，对睡眠前记忆进行额外衰减
        - 把特别老且 weight 很低的短期记忆标记为“只保留为长期统计，不再用于检索”
        """
        return
