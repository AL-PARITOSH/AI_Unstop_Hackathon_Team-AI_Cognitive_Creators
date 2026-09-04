import os
import math
import wave
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from moviepy.editor import ImageSequenceClip, AudioFileClip

def generate_talking_avatar_video(image_path: str, audio_path: str, output_path: str) -> bool:
    """
    Generate an animated talking/acting human AI Teacher avatar video MP4 with lip-sync and facial movement.
    """
    if not os.path.exists(image_path) or not os.path.exists(audio_path):
        return False

    try:
        # Load avatar image
        base_img = Image.open(image_path).convert("RGB")
        width, height = base_img.size

        # Get audio clip duration and audio samples
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        fps = 20
        num_frames = int(duration * fps)

        # Estimate mouth location (approx bottom-center of face: ~50% x, ~65% y)
        mouth_cx = int(width * 0.50)
        mouth_cy = int(height * 0.65)
        mouth_w = int(width * 0.14)
        mouth_h = int(height * 0.08)

        # Estimate eye locations (left eye ~40% x, 45% y; right eye ~60% x, 45% y)
        eye_y = int(height * 0.45)
        l_eye_x = int(width * 0.42)
        r_eye_x = int(width * 0.58)
        eye_r = int(width * 0.04)

        # Sample audio volume envelope safely for lip sync
        audio_data = audio_clip.to_soundarray()
        if len(audio_data.shape) > 1:
            audio_mono = np.abs(audio_data).mean(axis=1)
        else:
            audio_mono = np.abs(audio_data)

        audio_sr = audio_clip.fps or 44100
        raw_vols = []
        for f_idx in range(num_frames):
            s_idx = int(f_idx * audio_sr / fps)
            e_idx = min(len(audio_mono), int((f_idx + 1) * audio_sr / fps))
            chunk = audio_mono[s_idx:e_idx]
            raw_vols.append(float(chunk.mean()) if len(chunk) > 0 else 0.0)

        raw_vols = np.array(raw_vols)
        max_vol = np.max(raw_vols) if np.max(raw_vols) > 0 else 1.0
        norm_vol = raw_vols / max_vol

        frames = []

        for f_idx in range(num_frames):
            # 1. Micro head movement (subtle sine sway and tilt)
            shift_x = int(math.sin(f_idx / 8.0) * 3)
            shift_y = int(math.cos(f_idx / 12.0) * 2)

            frame = Image.new("RGB", (width, height), (15, 23, 42))
            frame.paste(base_img, (shift_x, shift_y))
            draw = ImageDraw.Draw(frame)

            # 2. Dynamic Lip-Sync Mouth Opening based on speech audio volume
            vol = norm_vol[min(f_idx, len(norm_vol) - 1)]
            mouth_open = int(vol * 14) # Open mouth height

            if mouth_open > 1:
                # Draw subtle mouth inner shadow / lip opening
                m_box = [
                    mouth_cx - mouth_w // 2 + shift_x,
                    mouth_cy - mouth_h // 4 + shift_y,
                    mouth_cx + mouth_w // 2 + shift_x,
                    mouth_cy + mouth_h // 4 + mouth_open + shift_y
                ]
                draw.ellipse(m_box, fill=(120, 40, 50))
                
                # Draw upper and lower lip contour curves
                draw.arc(m_box, start=0, end=180, fill=(180, 80, 90), width=2)
                draw.arc(m_box, start=180, end=360, fill=(160, 70, 80), width=2)

            # 3. Natural Eye Blinking (blink every ~60 frames)
            if (f_idx % 60) in [0, 1, 2]:
                # Draw closed eyelids
                draw.line([l_eye_x - eye_r + shift_x, eye_y + shift_y, l_eye_x + eye_r + shift_x, eye_y + shift_y], fill=(160, 120, 100), width=3)
                draw.line([r_eye_x - eye_r + shift_x, eye_y + shift_y, r_eye_x + eye_r + shift_x, eye_y + shift_y], fill=(160, 120, 100), width=3)

            np_frame = np.array(frame)
            frames.append(np_frame)

        print(f"Synthesizing {len(frames)} animated talking avatar frames...")
        video_clip = ImageSequenceClip(frames, fps=fps)
        video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(output_path, fps=fps, codec="libx264", audio_codec="aac", logger=None)
        audio_clip.close()
        video_clip.close()

        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print("TALKING AVATAR ANIMATOR ERROR:", e)
        return False

# Test run
if __name__ == "__main__":
    img = "media_cache/default_teacher_avatar.png"
    aud = "media_cache/test_voice.mp3"
    out = "media_cache/test_talking_avatar_local.mp4"
    res = generate_talking_avatar_video(img, aud, out)
    print("GENERATION SUCCESS:", res)
    if res:
        print("VIDEO FILE SIZE:", os.path.getsize(out), "bytes")
