"""
Edge-TTS Audio Narration Generator with Multilingual Voice Mapping and Caching.
"""

import os
import wave
import struct
import math
import asyncio
import hashlib
import logging
from typing import Tuple
from src.config import MEDIA_CACHE_DIR

logger = logging.getLogger(__name__)

VOICE_MAP = {
    ("Hindi", "female"): "hi-IN-SwaraNeural",
    ("Hindi", "male"): "hi-IN-MadhurNeural",
    ("Hinglish", "female"): "hi-IN-SwaraNeural",
    ("Hinglish", "male"): "hi-IN-MadhurNeural",
    ("English", "female"): "en-IN-NeerjaNeural",
    ("English", "male"): "en-IN-PrabhatNeural",
}

def get_voice(language: str = "Hinglish", gender: str = "female") -> str:
    lang_key = language.capitalize()
    if lang_key not in ["Hindi", "English", "Hinglish"]:
        lang_key = "Hinglish"
    gender_key = gender.lower() if gender.lower() in ["male", "female"] else "female"
    return VOICE_MAP.get((lang_key, gender_key), "hi-IN-SwaraNeural")


async def generate_tts_audio_async(text: str, voice: str, output_path: str):
    """Call Edge TTS to save narration MP3 file."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_tts_audio(text: str, language: str = "Hinglish", gender: str = "female", rate: str = "+0%") -> Tuple[str, float]:
    """
    Synchronous wrapper to generate TTS audio MP3 and calculate duration.
    Returns (mp3_file_path, duration_seconds).
    """
    voice = get_voice(language, gender)
    
    # Hash for caching
    hash_key = hashlib.md5(f"{text}_{voice}_{rate}".encode("utf-8")).hexdigest()
    output_filename = f"narration_{hash_key}.mp3"
    output_path = os.path.join(MEDIA_CACHE_DIR, output_filename)

    # Re-generate if missing or if existing file is a broken/corrupted small fallback (<2000 bytes)
    if not os.path.exists(output_path) or os.path.getsize(output_path) < 2000:
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception:
                pass

        try:
            logger.info(f"Generating Edge-TTS audio using voice {voice}...")
            asyncio.run(generate_tts_audio_async(text, voice, output_path))
        except Exception as e:
            logger.error(f"Edge-TTS generation failed: {e}. Creating fallback audio.")
            return create_fallback_audio(output_path, text)

    duration = get_audio_duration(output_path, text)
    return output_path, duration


def get_audio_duration(audio_path: str, text: str = "") -> float:
    """Estimate or measure audio duration in seconds (supporting MoviePy 1.x & 2.x)."""
    try:
        try:
            from moviepy.editor import AudioFileClip
        except ImportError:
            from moviepy import AudioFileClip

        clip = AudioFileClip(audio_path)
        dur = clip.duration
        clip.close()
        return float(dur)
    except Exception as e:
        logger.warning(f"Could not read exact audio clip duration: {e}")
        words = len(text.split())
        return max(3.0, float(words) / 2.3)


def create_fallback_audio(output_path: str, text: str) -> Tuple[str, float]:
    """Generate a valid audible WAV fallback file if TTS service fails."""
    wav_path = output_path.replace(".mp3", ".wav")
    duration = max(3.0, float(len(text.split())) / 2.3)
    sample_rate = 22050
    num_samples = int(sample_rate * duration)

    try:
        with wave.open(wav_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            # Generate soft warm sine tone (440Hz A tone)
            for i in range(num_samples):
                sample = int(1000.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
                wav_file.writeframes(struct.pack("<h", sample))
        return wav_path, duration
    except Exception as e:
        logger.error(f"Could not create fallback WAV audio file: {e}")
        return output_path, duration
