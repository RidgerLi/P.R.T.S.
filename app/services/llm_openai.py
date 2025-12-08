from app.services.llm_base import LlmBackend
from app.config import OPEN_API_KEY
from openai import OpenAI, RateLimitError, APIError
import logging

class LlmOpenaiBackend(LlmBackend):
    
    def __init__(self, model_name:str = "gpt-5-mini"):
        if not OPEN_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set. Check your .env file.")
        
        self.client = OpenAI(api_key=OPEN_API_KEY)
        self.model_name = model_name

    def chat(self, message: List[Dict]) -> str:
        try:
            by_response = False
            if by_response:
                print("发送输出：")
                print(message)
                response = self.client.responses.create(
                    model=self.model_name,
                    input=message,
                    # max_output_tokens=512,
                )

                print("获得ai输出：")
                print(response)

                # 官方推荐的写法：优先用 output_text
                ai_text = response.output_text

            else:
                print("发送输出：")
                print(message)
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=message,
                    # max_completion_tokens=256,
                )

                print("获得ai输出：")
                print(response)

                ai_text = response.choices[0].message.content

            # 保险起见，做个兜底
            if ai_text is None:
                # 手动找 output 里的 message 项
                for item in response.output or []:
                    if getattr(item, "type", None) == "message":
                        if item.content and len(item.content) > 0:
                            part = item.content[0]
                            # 有的 SDK 是 part.text，有的是 part["text"]
                            ai_text = getattr(part, "text", None) or getattr(part, "output_text", None)
                            if ai_text:
                                break

            if ai_text is None:
                ai_text = "（模型没有返回文本内容）"

            return ai_text

        except RateLimitError as e:
            logging.error(f"OpenAI quota exceeded: {e}")
            return "系统大模型配额不足！充值后使用！！"
        except APIError as e:
            logging.error(f"API Error: {e}")
            return "系统故障，api出现错误！"


    def chat_by_complete(self, message: List[Dict]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=message,
                max_completion_tokens=256,
            )

            print("获得ai输出：")
            print(response)

            ai_text = response.choices[0].message.content
            return ai_text or ""

        except RateLimitError as e:
            logging.error(f"OpenAI quota exceeded: {e}")
            return "系统大模型配额不足！充值后使用！！"

        except APIError as e:
            logging.error(f"API Error: {e}")
            return "系统故障，api出现错误！"
