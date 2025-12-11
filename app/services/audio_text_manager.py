# app/services/audio_io.py
from typing import Any
from io import BytesIO

from .ai_client import tts, stt

def run_stt(audio_bytes: bytes) -> str:
    reply = stt(audio_bytes)

    return reply


def run_tts(text: str) -> bytes:
    """
    文本转语音 (Text-to-Speech).
    """
    bytes = tts(text, "nova")
    return bytes


