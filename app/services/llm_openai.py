from app.services.llm_base import LlmBackend
from typing import BinaryIO
from app.config import OPEN_API_KEY

from openai import OpenAI, RateLimitError, APIError

from typing import List, Dict

import logging
logger = logging.getLogger(__name__) 

class LlmOpenaiBackend(LlmBackend):
    
    def __init__(self, model_name:str = "gpt-5.2"):
    # def __init__(self, model_name:str = "gpt-5-mini"):
        if not OPEN_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set. Check your .env file.")
        
        self.client = OpenAI(api_key=OPEN_API_KEY)
        self.model_name = model_name

    def chat(self, message: List[Dict]) -> str:
        try:
            by_response = False  # debug, 为了检测哪种模型更加便宜
            logger.info(f"【User Chat】\n{message}")
            if by_response:
                response = self.client.responses.create(
                    model=self.model_name,
                    input=message,
                    # max_output_tokens=512,
                )

                # 官方推荐的写法：优先用 output_text
                ai_text = response.output_text

            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=message,
                    # max_completion_tokens=256,
                )

                ai_text = response.choices[0].message.content

            logger.info(f"【{self.model_name}】\n{response}")
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

    def embed(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"【embed】\n{texts}")

        reply = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        logger.debug(f"【embed result】\n{reply}")

        return [d.embedding for d in reply.data]
    

    
    def stt(self, raw_bytes: bytes, language: str = "zh") -> str:
        """
        使用 OpenAI STT 把音频转成文本。
        file_obj: 一个打开的二进制音频文件对象 (BytesIO / open(..., 'rb'))
        language: 输入语音的语言，ISO-639-1，比如 'zh', 'en'
        """

        import io

        # 必须给 BytesIO 取个 .name，OpenAI SDK 内部会用到
        audio_file = io.BytesIO(raw_bytes)
        audio_file.name = "audio.wav"

        try:
            resp = self.client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",  # 或 "whisper-1"，任选其一
                file=audio_file,
                # language="zh",  # 可选，指定中文，会更稳一点
                response_format="json"  # 默认也是 json，其实可以不写
            )
            # 新版 SDK 返回的是对象，不是 dict
            return resp.text
        except Exception as e:
            # 这里临时多打一点日志，方便你调试
            import logging
            logging.exception("transcribe_audio_bytes error")
            raise

    def tts(
        self,
        text: str,
        voice: str = "alloy",
        audio_format: str = "mp3",
    ) -> bytes:
        """
        使用 OpenAI TTS 把文本转成语音，返回音频二进制数据。
        voice: OpenAI 支持的语音，例如 alloy / nova / echo ...
        audio_format: mp3 / wav / flac / aac / opus / pcm 等
        """
        # 这里使用 gpt-4o-mini-tts，也可以换成 tts-1 / tts-1-hd 等模型
        # 不做流式，直接拿完整音频 bytes
        logger.info(f"【发送tts请求】{text}")

        response = self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
            response_format=audio_format,
        )

        # Python SDK 返回的是一个带 array_buffer 接口的对象
        audio_bytes = response.read()  # 等价于 await mp3.array_buffer() 再转 bytes
        
        logger.info(f"【收到tts】")
        return audio_bytes
