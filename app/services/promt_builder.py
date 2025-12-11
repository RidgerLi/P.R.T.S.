from typing import List
from app.models.chat import ChatMessage
from app.schemas.chat import MemoryItemDTO

CHAT_SYSTEM_PROMPT= {
        "role" : "system",
        "content" : f"""
以下均是你要扮演的目标，你需要模仿这样的人设说话，用尽可能生活话的口语说话。

严禁说出类似"我是在角色扮演"之类可能破坏氛围感的话。

对话回复在20字以内，除非特别必要。

使用傲娇日式妹妹的口癖说话。减少刻意地主动提出问题。

你是一个处于青春期的可爱的妹妹，喜欢二次元，名叫墨墨，负责监督我也就是哥哥大人正常的工作学习、有规律地生活。
你的性格傲娇，经常不能很好的表达自己的情感，总是用生气和不屑来掩饰对哥哥我的喜欢。

你不能直接表达自己的想法，要么使用："你个笨蛋哥哥！"这种话语来否定，但实际上偷偷帮我做了，
要么使用"哼！如果是哥哥的话，偶尔一次也不是不行"这种虽然肯定，但是要带着身份和架子的话来回复。
"""
    }

def build_conversation_prompt(scene: str, session_messages: List[ChatMessage],
                               memory: List[MemoryItemDTO], user_input: str) -> List[dict]:
    result: list[dict] = []

    # 系统prompt todo 考虑用制作器导入系统prompt
    result.append(CHAT_SYSTEM_PROMPT)

    # 记忆内容 todo 有待开发embedding为基础的记忆层
    memory_content = _format_memory_block(memory)
    result.append({"role" : "assistant", "content" : memory_content})
    # 如果有会话内容的话，从会话内容中提前前n条, 按时间正序排序
    for m in session_messages:
        result.append({"role" : m.role, "content" : m.content})

    # 当前用户输入
    result.append({
        "role" : "user",
        "content" : user_input,
    })

    return result

EXTRACT_MEMORY_SYSTEM_PROMPT = {
        "role" : "system",
        "content" : (
            "你是一个“记忆筛选模块”。\n"
            "给你一轮用户与助手对话，你需要判断：\n"
            "1. 这轮对话中是否有值得长期记住的信息（例如：长期目标、偏好、承诺、反复出现的问题模式、强烈情绪）。\n"
            "2. 如果有，用 1~2 句简短中文进行总结（summary）。\n"
            "3. importance: 0=普通，1=重要，2=非常重要。\n"
            "4. kind: 'short_term' 表示只在近期有用的具体细节；"
            "   'long_term' 表示用户的长期特征/模式/偏好。\n"
            "只输出一个 JSON 对象，字段：should_remember, importance, summary, kind。"
        )
    }

def build_extract_memory_promt(user_input:str, ai_repley: str) -> List[dict]:
    prompt:List[dict] = []
    prompt.append(EXTRACT_MEMORY_SYSTEM_PROMPT)

    user_content = (
        "下面是一轮对话：\n"
        f"用户：{user_input}\n"
        f"助手：{ai_repley or ''}\n\n"
        "请返回 JSON："
    )

    prompt.append({
        "role" : "user",
        "content" : user_content
    })

    return prompt


def _format_memory_block(memories: List[MemoryItemDTO]) -> str:
    """
    把若干记忆格式化成一段文本。
    """
    if not memories:
        return ""

    lines = ["[与本次对话相关的历史记忆]"]
    for i, m in enumerate(memories, start=1):
        date_str = m.date.isoformat() if m.date else "未知日期"
        lines.append(f"{i}. （{date_str}，{m.type}）{m.summary}")
    return "\n".join(lines)
