# app/emb_local.py

# app/emb_local.py
import logging
from typing import List

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "BAAI/bge-small-zh-v1.5"
emb_model = SentenceTransformer(MODEL_NAME, device="cpu")
logger.info(f"Loaded local embedding model: {MODEL_NAME}")


def embed_texts_local(texts: List[str]) -> List[List[float]]:
    """
    批量计算文本 embedding，返回 List[List[float]]，
    每一条都是一个向量。
    """
    if not texts:
        return []

    embs = emb_model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,  # 如果你要余弦相似度，这个很方便
    )
    # embs 是 np.ndarray(shape=(N, D))
    # 转成 List[List[float]]
    return embs.tolist()


def embed_text_local(text: str) -> List[float]:
    """
    单条文本 embedding，返回 List[float]。
    """
    if not text:
        dim = emb_model.get_sentence_embedding_dimension()
        return [0.0] * dim

    return embed_texts_local([text])[0]
