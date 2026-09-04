"""
FFmpeg / MoviePy Video Compositor combining Whiteboard Visuals (65%), Avatar (35%), Audio, and SRT Subtitles.
"""

import os
import hashlib
import subprocess
import logging
from typing import Optional, Tuple
from src.config import MEDIA_CACHE_DIR
from src.avatar_service import TEACHER_AVATAR_IMAGE, generate_sadtalker_avatar_video

logger = logging.getLogger(__name__)

def check_ffmpeg_available() -> bool:
    """Check if system FFmpeg CLI is accessible."""
    try:
        res = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode == 0
    except Exception:
        return False


def generate_srt_subtitles(text: str, duration: float, srt_path: str):
    """Generate simple SRT subtitle file matching narration text and duration."""
    words = text.split()
    if not words:
        words = ["Lesson"]

    chunk_size = max(1, len(words) // 3)
    lines = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    num_lines = len(lines)
    time_per_line = duration / num_lines

    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, line in enumerate(lines):
            start_sec = idx * time_per_line
            end_sec = (idx + 1) * time_per_line

            def format_time(s):
                hrs = int(s // 3600)
                mins = int((s % 3600) // 60)
                secs = int(s % 60)
                ms = int((s - int(s)) * 1000)
                return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

            f.write(f"{idx + 1}\n")
            f.write(f"{format_time(start_sec)} --> {format_time(end_sec)}\n")
            f.write(f"{line}\n\n")


def compose_with_moviepy(visual_image_path: str, right_media_path: str, audio_path: str, audio_duration: float, output_mp4: str) -> bool:
    """Version-agnostic MoviePy video compositor supporting MoviePy 1.x and 2.x."""
    try:
        try:
            from moviepy.editor import ImageClip, VideoFileClip, AudioFileClip, clips_array
        except ImportError:
            from moviepy import ImageClip, VideoFileClip, AudioFileClip, clips_array
        
        dur = max(2.0, audio_duration)

        # Handle API differences between MoviePy 1.x and 2.x
        if hasattr(ImageClip, 'with_duration'):
            # MoviePy 2.x API
            img_left = ImageClip(visual_image_path).with_duration(dur).resized(height=720)
            if right_media_path.endswith(".mp4") and os.path.exists(right_media_path) and os.path.getsize(right_media_path) > 1000:
                img_right = VideoFileClip(right_media_path).with_duration(dur).resized(height=720)
            else:
                img_right = ImageClip(right_media_path).with_duration(dur).resized(height=720)
            combo = clips_array([[img_left, img_right]])
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                audio = AudioFileClip(audio_path)
                combo = combo.with_audio(audio)
        else:
            # MoviePy 1.x API
            img_left = ImageClip(visual_image_path).set_duration(dur).resize(height=720)
            if right_media_path.endswith(".mp4") and os.path.exists(right_media_path) and os.path.getsize(right_media_path) > 1000:
                img_right = VideoFileClip(right_media_path).set_duration(dur).resize(height=720)
            else:
                img_right = ImageClip(right_media_path).set_duration(dur).resize(height=720)
            combo = clips_array([[img_left, img_right]])
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                audio = AudioFileClip(audio_path)
                combo = combo.set_audio(audio)

        logger.info("Writing video segment via MoviePy...")
        combo.write_videofile(output_mp4, fps=15, codec="libx264", audio_codec="aac", logger=None)
        return os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 0
    except Exception as e:
        logger.warning(f"MoviePy composition failed: {e}")
        return False


def compose_lesson_segment_video(
    visual_image_path: str,
    audio_path: str,
    audio_duration: float,
    spoken_text: str,
    avatar_video_path: Optional[str] = None
) -> Tuple[Optional[str], str]:
    """
    Compose segment video MP4 (1280x720) combining:
    - Left 65%: Visual whiteboard image
    - Right 35%: Avatar video or teacher portrait card
    - Subtitles & Audio track
    Returns (video_path, status_message).
    """
    # Attempt to fetch SadTalker avatar video if not provided
    if not avatar_video_path:
        fetched_avatar, _ = generate_sadtalker_avatar_video(audio_path, timeout_sec=20)
        if fetched_avatar:
            avatar_video_path = fetched_avatar

    right_media = avatar_video_path or TEACHER_AVATAR_IMAGE

    hash_key = hashlib.md5(f"{visual_image_path}_{audio_path}_{spoken_text}_{right_media}".encode("utf-8")).hexdigest()[:12]
    output_mp4 = os.path.join(MEDIA_CACHE_DIR, f"segment_{hash_key}.mp4")
    srt_path = os.path.join(MEDIA_CACHE_DIR, f"subtitles_{hash_key}.srt")

    if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 0:
        return output_mp4, "Cached video segment loaded."

    generate_srt_subtitles(spoken_text, audio_duration, srt_path)

    # Attempt 1: System FFmpeg CLI
    if check_ffmpeg_available():
        try:
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", visual_image_path,
                "-loop", "1" if not right_media.endswith(".mp4") else "0", "-i", right_media,
                "-i", audio_path,
                "-filter_complex",
                "[0:v]scale=832:720:force_original_aspect_ratio=increase,crop=832:720[left];"
                "[1:v]scale=448:720:force_original_aspect_ratio=increase,crop=448:720[right];"
                "[left][right]hstack=inputs=2[v]",
                "-map", "[v]",
                "-map", "2:a",
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-c:a", "aac",
                "-b:a", "1920k",
                "-t", str(audio_duration),
                "-pix_fmt", "yuv420p",
                output_mp4
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45)
            if res.returncode == 0 and os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 0:
                return output_mp4, "Lesson video segment composed successfully via FFmpeg CLI."
        except Exception as e:
            logger.warning(f"System FFmpeg failed, trying MoviePy fallback: {e}")

    # Attempt 2: MoviePy backend compositor
    if compose_with_moviepy(visual_image_path, right_media, audio_path, audio_duration, output_mp4):
        return output_mp4, "Lesson video segment composed successfully via MoviePy."

    return None, "Audio-visual lesson mode active."
