"""
Speech-to-Text Transcription Service via Groq Whisper and Local faster-whisper Fallback.
"""

import os
import logging
from typing import Optional
from src.config import GROQ_STT_MODEL, GROQ_API_KEY
from src.llm_service import get_groq_client

logger = logging.getLogger(__name__)

_faster_whisper_model = None

def get_local_whisper():
    global _faster_whisper_model
    if _faster_whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            _faster_whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        except Exception as e:
            logger.warning(f"Local faster-whisper not available: {e}")
            _faster_whisper_model = "unavailable"
    return _faster_whisper_model


def transcribe_audio(audio_file_path: str, language: str = "en") -> str:
    """
    Transcribe audio using Groq API (whisper-large-v3) with local faster-whisper fallback.
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Primary: Groq Whisper API
    if GROQ_API_KEY:
        try:
            logger.info("Transcribing audio using Groq Whisper API...")
            client = get_groq_client()
            with open(audio_file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), audio_file.read()),
                    model=GROQ_STT_MODEL,
                    response_format="json",
                    temperature=0.0
                )
            return transcription.text.strip()
        except Exception as e:
            logger.warning(f"Groq STT transcription failed, trying local fallback: {e}")

    # Secondary: Local faster-whisper fallback
    whisper_model = get_local_whisper()
    if whisper_model != "unavailable":
        try:
            logger.info("Transcribing audio using local faster-whisper model...")
            segments, info = whisper_model.transcribe(audio_file_path, beam_size=2)
            transcribed_text = " ".join([segment.text for segment in segments]).strip()
            return transcribed_text
        except Exception as e:
            logger.error(f"Local faster-whisper transcription failed: {e}")

    raise RuntimeError("Speech-to-text service is currently unavailable. Please type your response.")
