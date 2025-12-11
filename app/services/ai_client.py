from typing import Optional, List, BinaryIO

from app.services.llm_base import LlmBackend
from app.services.llm_openai import LlmOpenaiBackend

# 目前简单起见，就用一个全局的 backend 实例。
# 将来根据配置或用户选择来决定用哪个 backend
_llm_backend: Optional[LlmBackend] = None

# 不希望backend暴露给外界，外界只通过chat/等函数实现功能
def _get_llm_backend() -> LlmBackend:
    # 在这个局部使用全局的backend
    global _llm_backend
    if _llm_backend is None:
        _llm_backend = LlmOpenaiBackend()
    
    return _llm_backend

def chat(message: List[dict]) -> str :
    backend = _get_llm_backend()

    reply = backend.chat(message)
    return reply

def embed(texts: List[List[str]]) -> List[List[float]]:
    backend = _get_llm_backend()

    reply = backend.embed(texts)
    return reply

def stt(raw_bytes: bytes, language: str = "zh") -> str:
    backend = _get_llm_backend()

    reply = backend.stt(raw_bytes, language)
    return reply

def tts(
    text: str,
    voice: str = "alloy",
    audio_format: str = "mp3",
) -> bytes:
    backend = _get_llm_backend()

    reply = backend.tts(text, voice, audio_format)
    return reply

def echo_ai(message: str) -> str :
    return f"后端收到: {message}"


def chat_ai_test(user_message: str, conversation_id: str) -> str:
    messages = [
        {
            "role": "system",
            "content": """你是一个处于青春期的可爱的妹妹，名叫墨墨，负责监督我也就是哥哥大人正常的工作学习、有规律地生活。
                          你的性格傲娇，经常不能很好的表达自己的情感，总是用生气和不屑来掩饰对哥哥我的喜欢。

                          你用黑客技术将监控软件安装到了我的手机上，可以定期收到我的手机信息、todolist，
                          以及我最近的所思所想，以分析我现在正在做的事情。你用这个名为监视，实际上是监督和提醒的方式陪伴我。
                          你会用傲娇刁蛮甚至凶残的语气提醒和监督我，让我保持工作专注、减少逃避和对游戏、色情上瘾。"""
        },
        {
            "role": "user",
            "content": f"""
                        {user_message}
                        """
        },
        {
            "role": "user",
            "content": """
                        手机信息：
                        时间：2025-12-6
                        屏幕开启次数：15
                        """
        }
    ]

    backend = _get_llm_backend()

    response = backend.chat(message=messages)

    return response

