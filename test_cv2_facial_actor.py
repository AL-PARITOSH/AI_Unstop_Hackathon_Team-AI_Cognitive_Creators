import os
import cv2
import math
import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip

def generate_opencv_talking_avatar(image_path: str, audio_path: str, output_path: str) -> bool:
    """
    Generate high-realism audio-driven talking human AI Teacher avatar video MP4 using OpenCV face tracking.
    """
    if not os.path.exists(image_path) or not os.path.exists(audio_path):
        return False

    try:
        # Load image
        img_bgr = cv2.imread(image_path)
        h, w, c = img_bgr.shape

        # Detect face via OpenCV Haar Cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            fx, fy, fw, fh = faces[0]
            mouth_cx = fx + fw // 2
            mouth_cy = fy + int(fh * 0.72)
            mouth_w = int(fw * 0.35)
            mouth_h = int(fh * 0.16)

            eye_y = fy + int(fh * 0.40)
            l_eye_x = fx + int(fw * 0.30)
            r_eye_x = fx + int(fw * 0.70)
            eye_w = int(fw * 0.20)
            eye_h = int(fh * 0.10)
        else:
            mouth_cx = int(w * 0.50)
            mouth_cy = int(h * 0.55)
            mouth_w = int(w * 0.20)
            mouth_h = int(h * 0.08)
            eye_y = int(h * 0.42)
            l_eye_x = int(w * 0.40)
            r_eye_x = int(w * 0.60)
            eye_w = int(w * 0.12)
            eye_h = int(h * 0.06)

        # Extract skin color around mouth/chin for seamless blending
        skin_sample = img_bgr[max(0, mouth_cy - 10):min(h, mouth_cy + 10), max(0, mouth_cx - 10):min(w, mouth_cx + 10)]
        avg_bgr = skin_sample.mean(axis=(0, 1)).astype(int).tolist() if skin_sample.size > 0 else [180, 160, 150]
        lip_color = (max(0, avg_bgr[0]-40), max(0, avg_bgr[1]-50), min(255, avg_bgr[2]+20)) # Natural lip tone

        # Get audio envelope
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        fps = 20
        num_frames = int(duration * fps)

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

        frames_rgb = []

        for f_idx in range(num_frames):
            # Head sway and subtle nod
            angle = math.sin(f_idx / 10.0) * 1.5
            shift_x = int(math.sin(f_idx / 8.0) * 2)
            shift_y = int(math.cos(f_idx / 12.0) * 2)

            M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            M[0, 2] += shift_x
            M[1, 2] += shift_y
            frame = cv2.warpAffine(img_bgr, M, (w, h), borderMode=cv2.BORDER_REFLECT)

            vol = norm_vol[min(f_idx, len(norm_vol) - 1)]
            open_h = int(vol * (mouth_h * 0.7))

            # 1. Animate Mouth Opening & Lip-Sync
            if open_h > 2:
                # Draw dark oral cavity
                m_center = (mouth_cx + shift_x, mouth_cy + shift_y)
                cv2.ellipse(frame, m_center, (mouth_w // 2, open_h), 0, 0, 360, (20, 15, 25), -1)
                # Draw upper and lower lips
                cv2.ellipse(frame, (m_center[0], m_center[1] - open_h // 2), (mouth_w // 2, 4), 0, 0, 360, lip_color, 2)
                cv2.ellipse(frame, (m_center[0], m_center[1] + open_h // 2), (mouth_w // 2, 4), 0, 0, 360, lip_color, 2)

            # 2. Animate Eye Blinking (blink every 50-60 frames)
            if (f_idx % 55) in [0, 1, 2]:
                cv2.line(frame, (l_eye_x - eye_w // 2 + shift_x, eye_y + shift_y), (l_eye_x + eye_w // 2 + shift_x, eye_y + shift_y), avg_bgr, 3)
                cv2.line(frame, (r_eye_x - eye_w // 2 + shift_x, eye_y + shift_y), (r_eye_x + eye_w // 2 + shift_x, eye_y + shift_y), avg_bgr, 3)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames_rgb.append(rgb)

        video_clip = ImageSequenceClip(frames_rgb, fps=fps)
        if hasattr(video_clip, 'set_audio'):
            video_clip = video_clip.set_audio(audio_clip)
        else:
            video_clip = video_clip.with_audio(audio_clip)

        video_clip.write_videofile(output_path, fps=fps, codec="libx264", audio_codec="aac", logger=None)
        audio_clip.close()
        video_clip.close()

        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print("OPENCV AVATAR GENERATION ERROR:", e)
        return False

if __name__ == "__main__":
    res = generate_opencv_talking_avatar('media_cache/default_teacher_avatar.png', 'media_cache/test_voice.mp3', 'media_cache/test_cv2_talking.mp4')
    print("CV2 TALKING AVATAR GENERATION SUCCESS:", res)
    if res:
        print("GENERATED FILE SIZE:", os.path.getsize('media_cache/test_cv2_talking.mp4'))
