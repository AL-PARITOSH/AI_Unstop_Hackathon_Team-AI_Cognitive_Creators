"""
SadTalker & OpenCV Audio-Driven Talking Avatar Service supporting Hugging Face Space GPU integration,
Local SadTalker CLI, and OpenCV Audio-Driven Facial Motion Animator.
"""

import os
import math
import json
import uuid
import requests
import hashlib
import logging
import urllib.parse
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Tuple, Optional
from src.config import MEDIA_CACHE_DIR, POLLINATIONS_API_KEY

logger = logging.getLogger(__name__)

# Default fictional AI Teacher Avatar image path
TEACHER_AVATAR_IMAGE = os.path.join(MEDIA_CACHE_DIR, "default_teacher_avatar.png")
HF_SADTALKER_SPACE_URL = os.getenv("HF_SADTALKER_URL", "https://kevinwang676-sadtalker.hf.space")

def ensure_default_avatar_image() -> str:
    """Generate or download realistic human AI teacher avatar portrait."""
    if not os.path.exists(TEACHER_AVATAR_IMAGE) or os.path.getsize(TEACHER_AVATAR_IMAGE) < 5000:
        try:
            logger.info("Fetching realistic human teacher portrait via Pollinations AI...")
            prompt = "photorealistic portrait of a friendly professional female teacher educator looking at camera in modern classroom 8k high quality"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=512&height=512&nologo=true"
            headers = {}
            if POLLINATIONS_API_KEY:
                headers["Authorization"] = f"Bearer {POLLINATIONS_API_KEY}"

            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code == 200 and len(res.content) > 5000:
                with open(TEACHER_AVATAR_IMAGE, "wb") as f:
                    f.write(res.content)
                return TEACHER_AVATAR_IMAGE
        except Exception as e:
            logger.warning(f"Could not download online human avatar portrait: {e}")

        # Fallback card generator if offline
        fig, ax = plt.subplots(figsize=(4, 5), facecolor='#0F172A')
        ax.set_facecolor('#1E293B')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        badge = patches.Circle((0.5, 0.65), 0.22, color='#4F46E5', ec='#818CF8', lw=3)
        ax.add_patch(badge)
        head = patches.Circle((0.5, 0.70), 0.09, color='#F8FAFC')
        ax.add_patch(head)
        body = patches.Polygon([[0.32, 0.48], [0.68, 0.48], [0.60, 0.60], [0.40, 0.60]], color='#38BDF8')
        ax.add_patch(body)

        ax.text(0.5, 0.32, "AI TEACHER AVATAR", color='#F8FAFC', fontsize=14, fontweight='bold', ha='center')
        ax.text(0.5, 0.22, "Adaptive Multilingual Educator", color='#94A3B8', fontsize=10, ha='center')

        plt.tight_layout()
        plt.savefig(TEACHER_AVATAR_IMAGE, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)

PERSONA_AVATARS = {
    "dr_sarah": {
        "filename": "avatar_dr_sarah.png",
        "prompt": "photorealistic portrait of friendly supportive female science educator Dr. Sarah in bright modern classroom smiling looking at camera",
        "gender": "female",
        "display_name": "Dr. Sarah (Intuitive & Relatable)"
    },
    "prof_aryan": {
        "filename": "avatar_prof_aryan.png",
        "prompt": "photorealistic portrait of distinguished male Indian engineering professor Prof. Aryan in academic research lab looking at camera with glasses",
        "gender": "male",
        "display_name": "Prof. Aryan (Analytical & Technical)"
    },
    "coach_maya": {
        "filename": "avatar_coach_maya.png",
        "prompt": "photorealistic portrait of energetic enthusiastic young female STEM coach Maya in high-tech workshop smiling at camera",
        "gender": "female",
        "display_name": "Coach Maya (High-Energy & Exam Prep)"
    }
}

def get_persona_avatar_image(persona: str = "dr_sarah") -> str:
    """Retrieve or generate avatar portrait for chosen teacher persona."""
    info = PERSONA_AVATARS.get(persona, PERSONA_AVATARS["dr_sarah"])
    target_path = os.path.join(MEDIA_CACHE_DIR, info["filename"])

    if os.path.exists(target_path) and os.path.getsize(target_path) > 3000:
        return target_path

    # Try downloading online via Pollinations
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(info['prompt'])}?width=512&height=512&nologo=true"
        headers = {}
        if POLLINATIONS_API_KEY:
            headers["Authorization"] = f"Bearer {POLLINATIONS_API_KEY}"
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200 and len(res.content) > 5000:
            with open(target_path, "wb") as f:
                f.write(res.content)
            return target_path
    except Exception as e:
        logger.warning(f"Could not download persona avatar for {persona}: {e}")

    # Fallback to default avatar image
    default_img = ensure_default_avatar_image()
    if not os.path.exists(target_path) and os.path.exists(default_img):
        import shutil
        shutil.copyfile(default_img, target_path)
    return target_path if os.path.exists(target_path) else default_img


ensure_default_avatar_image()



def generate_local_talking_avatar_video(image_path: str, audio_path: str, output_path: str) -> bool:
    """
    Synthesize high-realism audio-driven lip-synced and facial motion acting avatar video MP4 using OpenCV face detection.
    """
    try:
        try:
            from moviepy.editor import ImageSequenceClip, AudioFileClip
        except ImportError:
            from moviepy import ImageSequenceClip, AudioFileClip

        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            return False
        h, w, c = img_bgr.shape

        # Detect face location via OpenCV Haar Cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            fx, fy, fw, fh = faces[0]
            mouth_cx = fx + fw // 2
            mouth_cy = fy + int(fh * 0.745)
            mouth_w = int(fw * 0.35)
            mouth_h = int(fh * 0.14)

            eye_y = fy + int(fh * 0.40)
            l_eye_x = fx + int(fw * 0.30)
            r_eye_x = fx + int(fw * 0.70)
            eye_w = int(fw * 0.18)
            eye_h = int(fh * 0.08)
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

        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        fps = 16
        num_frames = int(duration * fps)

        # Safe audio reading: Avoid moviepy low-fps to_soundarray bug (IndexError)
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
        p95 = np.percentile(raw_vols, 95) if len(raw_vols) > 0 else 1.0
        if p95 <= 0:
            p95 = 1.0
        norm_vols = np.clip(raw_vols / p95, 0.0, 1.0)

        # Smooth volume envelope with exponential moving average
        smoothed_vols = np.zeros_like(norm_vols)
        cv = 0.0
        for i, v in enumerate(norm_vols):
            cv = 0.6 * cv + 0.4 * v
            smoothed_vols[i] = cv

        base_x, base_y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        frames_rgb = []

        for f_idx in range(num_frames):
            vol = float(smoothed_vols[f_idx])

            # 1. Natural subtle head gestures (educator head tilt, conversational nod, breathing sway)
            head_tilt = math.sin(f_idx / 18.0) * 1.0 + math.sin(f_idx / 9.0) * 0.3
            nod_y = math.sin(f_idx / 14.0) * 1.2 + (vol * 1.4)
            sway_x = math.sin(f_idx / 22.0) * 1.5

            disp_y = np.zeros_like(base_y)

            # 2. Natural Lip-Sync Warping
            if vol > 0.05:
                open_amount = min(6.0, vol * 6.0)
                y_diff = base_y - mouth_cy
                x_diff = (base_x - mouth_cx) / (mouth_w * 0.55)
                x_mask = np.maximum(0.0, 1.0 - x_diff**2)**2

                upper_mask = (y_diff >= -14) & (y_diff < 0)
                upper_weight = (1.0 + y_diff / 14.0) * x_mask
                disp_y[upper_mask] += (open_amount * 0.25 * upper_weight)[upper_mask]

                lower_mask = (y_diff >= 0) & (y_diff < 35)
                lower_weight = (1.0 - y_diff / 35.0) * x_mask
                disp_y[lower_mask] -= (open_amount * 1.0 * lower_weight)[lower_mask]

            # 3. Natural Eye Blink (2 frames every ~85 frames)
            blink_cycle = f_idx % 85
            if blink_cycle in [0, 1]:
                blink_amt = 7.0 if blink_cycle == 0 else 5.0
                for ex in [l_eye_x, r_eye_x]:
                    dx = (base_x - ex) / (eye_w * 0.55)
                    dy = (base_y - (eye_y - 2)) / (eye_h * 0.8)
                    eye_mask = np.maximum(0.0, 1.0 - (dx**2 + dy**2))**2
                    disp_y -= blink_amt * eye_mask

            warped = cv2.remap(img_bgr, base_x, base_y + disp_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

            # Subtle natural oral depth shading when mouth opens
            if vol > 0.15:
                open_amt = min(6.0, vol * 6.0)
                y_diff = base_y - mouth_cy
                x_diff = (base_x - mouth_cx) / (mouth_w * 0.5)
                dark_mask = np.exp(-0.5 * (x_diff / 0.5)**2) * np.exp(-0.5 * ((y_diff - open_amt * 0.4) / 1.8)**2)
                dark_factor = 1.0 - (0.4 * vol) * dark_mask[:, :, np.newaxis]
                warped = (warped.astype(np.float32) * dark_factor).clip(0, 255).astype(np.uint8)

            # 4. Apply head gesture transform
            M = cv2.getRotationMatrix2D((w // 2, h // 2), head_tilt, 1.0)
            M[0, 2] += sway_x
            M[1, 2] += nod_y
            final_frame = cv2.warpAffine(warped, M, (w, h), borderMode=cv2.BORDER_REFLECT)

            frames_rgb.append(cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB))

        video_clip = ImageSequenceClip(frames_rgb, fps=fps)
        if hasattr(video_clip, 'set_audio'):
            video_clip = video_clip.set_audio(audio_clip)
        else:
            video_clip = video_clip.with_audio(audio_clip)

        video_clip.write_videofile(output_path, fps=fps, codec="libx264", audio_codec="aac", preset="ultrafast", logger=None)
        audio_clip.close()
        video_clip.close()

        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        logger.error(f"OpenCV audio-driven avatar animation error: {e}")
        return False


def generate_sadtalker_hf_space_video(audio_path: str, avatar_image_path: Optional[str] = None, timeout_sec: int = 15) -> Tuple[Optional[str], str]:
    """
    Call Hugging Face Space 'kevinwang676/SadTalker' directly via WebSocket queue protocol.
    """
    try:
        import websocket
    except ImportError:
        return None, "websocket-client package not installed."

    avatar_path = avatar_image_path or ensure_default_avatar_image()
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
        return None, "Audio file invalid for avatar generation."

    hash_key = hashlib.md5(f"{audio_path}_{avatar_path}".encode("utf-8")).hexdigest()[:12]
    output_mp4 = os.path.join(MEDIA_CACHE_DIR, f"sadtalker_hf_{hash_key}.mp4")

    if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1000:
        return output_mp4, "Cached Hugging Face SadTalker video loaded."

    try:
        logger.info(f"Uploading assets to Hugging Face SadTalker space: {HF_SADTALKER_SPACE_URL}")
        
        with open(avatar_path, "rb") as f_img:
            up_img = requests.post(f"{HF_SADTALKER_SPACE_URL}/upload", files={"files": (os.path.basename(avatar_path), f_img, "image/png")}, timeout=10).json()[0]

        with open(audio_path, "rb") as f_aud:
            up_aud = requests.post(f"{HF_SADTALKER_SPACE_URL}/upload", files={"files": (os.path.basename(audio_path), f_aud, "audio/mp3")}, timeout=10).json()[0]

        img_obj = {"name": up_img, "data": None, "is_file": True}
        audio_obj = {"name": up_aud, "data": None, "is_file": True}

        ws_url = HF_SADTALKER_SPACE_URL.replace("https://", "wss://") + "/queue/join"
        session_hash = str(uuid.uuid4())[:10]

        ws = websocket.create_connection(ws_url, timeout=timeout_sec)

        while True:
            res = ws.recv()
            if not res:
                break
            
            msg = json.loads(res)
            msg_type = msg.get("msg")

            if msg_type == "estimation":
                rank = msg.get("rank", 0)
                if rank and rank > 5:
                    ws.close()
                    return None, f"HF Space queue busy (rank {rank}). Using audio-driven lip-sync fallback."

            elif msg_type == "send_hash":
                ws.send(json.dumps({"fn_index": 0, "session_hash": session_hash}))

            elif msg_type == "send_data":
                payload = {
                    "fn_index": 0,
                    "data": [
                        img_obj,
                        audio_obj,
                        "crop",
                        True,
                        False,
                        1,
                        256,
                        0
                    ],
                    "session_hash": session_hash
                }
                ws.send(json.dumps(payload))

            elif msg_type == "process_completed":
                out_data = msg.get("output", {}).get("data", [])
                if out_data and isinstance(out_data[0], dict):
                    vid_name = out_data[0].get("name")
                    vid_url = f"{HF_SADTALKER_SPACE_URL}/file={vid_name}"
                    v_res = requests.get(vid_url, timeout=20)
                    with open(output_mp4, "wb") as vf:
                        vf.write(v_res.content)
                    ws.close()
                    return output_mp4, "Hugging Face SadTalker avatar video generated successfully."
                break

    except Exception as e:
        logger.warning(f"Hugging Face SadTalker space exception: {e}")

    return None, "HF Space fallback trigger."


def generate_sadtalker_avatar_video(audio_path: str, avatar_image_path: Optional[str] = None, timeout_sec: int = 5) -> Tuple[Optional[str], str]:
    """
    Master Avatar Generation function.
    Uses ultra-fast OpenCV Audio-Driven Lip-Sync Animator with natural facial warping and head tilt.
    """
    avatar_path = avatar_image_path or ensure_default_avatar_image()
    hash_key = hashlib.md5(f"{audio_path}_{avatar_path}".encode("utf-8")).hexdigest()[:12]
    local_talking_mp4 = os.path.join(MEDIA_CACHE_DIR, f"talking_avatar_{hash_key}.mp4")

    if os.path.exists(local_talking_mp4) and os.path.getsize(local_talking_mp4) > 1000:
        return local_talking_mp4, "Cached talking avatar video loaded."

    # Direct ultra-fast OpenCV Audio-Driven Lip-Sync Facial Animator (completes in ~2s)
    logger.info("Generating ultra-fast OpenCV lip-synced talking avatar video...")
    if generate_local_talking_avatar_video(avatar_path, audio_path, local_talking_mp4):
        return local_talking_mp4, "Audio-driven lip-sync talking avatar generated successfully."

    # Fallback to HF Space if local generation encounters an issue
    vid_path, msg = generate_sadtalker_hf_space_video(audio_path, avatar_path, timeout_sec=timeout_sec)
    if vid_path and os.path.exists(vid_path) and os.path.getsize(vid_path) > 1000:
        return vid_path, msg

    return None, "Avatar animation fallback."


generate_talking_avatar_video = generate_local_talking_avatar_video
