from typing import List
from app.models.chat import ChatMessage

def build_conversation_prompt(session_messages: List[ChatMessage], user_input: str) -> List[dict]:
    result: list[dict] = []

    # 系统prompt todo 考虑用制作器导入系统prompt
    system_prompt = {
        "role" : "system",
        "content" : f"""你是一个处于青春期的可爱的妹妹，名叫墨墨，负责监督我也就是哥哥大人正常的工作学习、有规律地生活。
                          你的性格傲娇，经常不能很好的表达自己的情感，总是用生气和不屑来掩饰对哥哥我的喜欢。

                          你用黑客技术将监控软件安装到了我的手机上，可以定期收到我的手机信息、todolist，
                          以及我最近的所思所想，以分析我现在正在做的事情。你用这个名为监视，实际上是监督和提醒的方式陪伴我。
                          你会用傲娇刁蛮甚至凶残的语气提醒和监督我，让我保持工作专注、减少逃避和对游戏、色情上瘾。"""
    }
    result.append(system_prompt)

    # 记忆内容 todo 有待开发embedding为基础的记忆层

    # 如果有会话内容的话，从会话内容中提前前n条, 按时间正序排序
    for m in session_messages:
        result.append({"role" : m.role, "content" : m.content})

    # 当前用户输入
    result.append({
        "role" : "user",
        "content" : user_input,
    })

    return result
    