# app/stt_local_vosk.py
import io
import json
import logging
import wave

import vosk

logger = logging.getLogger(__name__)

# 1. 程序启动时加载一次模型（很关键，不要每次请求都 new）
#    路径改成你自己的模型目录
# VOSK_MODEL_PATH = "thirdparty/vosk-model-small-cn-0.22"
VOSK_MODEL_PATH = "thirdparty/vosk-model-cn-0.22"
vosk_model = vosk.Model(VOSK_MODEL_PATH)


def stt_wav_to_text_local(wav_bytes: bytes) -> str:
    """
    使用 Vosk 将 16k 单声道 16bit PCM WAV 字节流转成中文文本。
    失败返回空字符串。
    """
    try:
        # 2. 用 wave 从内存 bytes 里读 WAV 头 + 数据
        wf = wave.open(io.BytesIO(wav_bytes), "rb")

        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()

        # 你安卓那边是 16k 单声道 16bit PCM，这里简单校验下
        if channels != 1 or sampwidth != 2 or framerate != 16000:
            logger.warning(
                f"Unexpected WAV format: "
                f"channels={channels}, sampwidth={sampwidth}, framerate={framerate}"
            )

        rec = vosk.KaldiRecognizer(vosk_model, framerate)
        text_parts: list[str] = []

        # 3. 循环喂入数据
        while True:
            data = wf.readframes(4000)  # 每次读一点
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                # 中间结果
                res = json.loads(rec.Result())
                part = res.get("text", "")
                if part:
                    text_parts.append(part)

        # 4. 最终结果
        final = json.loads(rec.FinalResult())
        final_text = final.get("text", "")
        if final_text:
            text_parts.append(final_text)

        wf.close()

        full_text = "".join(text_parts).strip()
        logger.info(f"Vosk STT result: {full_text}")
        return full_text

    except Exception as e:
        logger.exception("Vosk local STT failed", exc_info=e)
        return ""
