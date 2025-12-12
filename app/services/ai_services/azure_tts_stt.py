import io
import wave
import azure.cognitiveservices.speech as speechsdk
from app.config import AZURE_SPEECH_KEY, SPEECH_REGION, PROJECT_ENDPOINT

import logging
logger = logging.getLogger(__name__)

VOICE_NAME = "zh-CN-Xiaoxiao:DragonHDFlashLatestNeural"
def stt_wav_to_text(wav_bytes: bytes) -> str:
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language = "zh-CN"
    speech_config.set_proxy("127.0.0.1", 18080)  # ✅

    # ✅ 从 wav 中解出 PCM
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        channels = wf.getnchannels()
        sample_rate = wf.getframerate()
        sampwidth = wf.getsampwidth()
        pcm = wf.readframes(wf.getnframes())

    if channels != 1 or sample_rate != 16000 or sampwidth != 2:
        logger.warning(f"WAV format unexpected: ch={channels}, sr={sample_rate}, sw={sampwidth}")

    stream_format = speechsdk.audio.AudioStreamFormat(
        samples_per_second=sample_rate,
        bits_per_sample=16,
        channels=channels
    )
    push_stream = speechsdk.audio.PushAudioInputStream(stream_format)
    push_stream.write(pcm)
    push_stream.close()

    audio_config = speechsdk.audio.AudioConfig(stream=push_stream)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    logger.info("正在识别语音...")
    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    if result.reason == speechsdk.ResultReason.NoMatch:
        return ""
    if result.reason == speechsdk.ResultReason.Canceled:
        try:
            c = speechsdk.CancellationDetails(result)
            logger.info(f"Canceled: {c.reason}, {c.error_details}")
        except Exception as e:
            logger.info(f"Canceled but read details failed: {e}")
        return ""
    return ""

def tts_text_to_mp3(text: str) -> bytes:
    """
    将文本 (str) 转化为 MP3 格式的音频字节流 (bytes)。
    """

    # 1. 配置
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY, 
        region=SPEECH_REGION
    )
    
    # 输出格式：MP3
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3
    )

    # 选择语音
    speech_config.speech_synthesis_voice_name = VOICE_NAME
    # speech_config.set_proxy("127.0.0.1", 7890)

    # 2. 不指定 audio_config，表示输出到内存（result.audio_data）
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=None
    )

    # 3. 执行合成
    logger.info(f"正在合成文本: {text[:20]}...")
    result = speech_synthesizer.speak_text_async(text).get()

    # 4. 处理结果
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        logger.info("合成成功，返回 MP3 字节流。")
        # ✅ 这里的 audio_data 已经是 MP3 字节
        return result.audio_data

    # 错误处理
    cancellation = speechsdk.CancellationDetails(result)
    logger.info(f"语音合成失败: Reason={cancellation.reason}")
    if cancellation.reason == speechsdk.CancellationReason.Error:
        logger.info(f"错误代码: {cancellation.error_code}")
        logger.info(f"错误细节: {cancellation.error_details}")
    return b''
