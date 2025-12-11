# app/services/audio_io.py
from .ai_services.azure_tts_stt import stt_wav_to_text, tts_text_to_mp3
import logging
logger = logging.getLogger(__name__)

def run_tts(text: str) -> bytes:
    """
    文本转语音 (Text-to-Speech).
    """
    logger.info(f"【tts running】")
    bytes = tts_text_to_mp3(text)
    return bytes

def run_stt(bytes: bytes) -> str:
    """
    文本转语音 (Text-to-Speech).
    """
    logger.info(f"【stt running】")
    text = stt_wav_to_text(bytes)
    return text
