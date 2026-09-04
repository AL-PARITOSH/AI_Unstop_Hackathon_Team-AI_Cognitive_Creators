import os
import json
import requests
import uuid
import websocket

url = "https://kevinwang676-sadtalker.hf.space"
ws_url = "wss://kevinwang676-sadtalker.hf.space/queue/join"
session_hash = str(uuid.uuid4())[:10]

img_path = "media_cache/default_teacher_avatar.png"
audio_path = "media_cache/test_voice.mp3"

if not os.path.exists(audio_path):
    import asyncio, edge_tts
    asyncio.run(edge_tts.Communicate("Namaste! Today we learn Ohm Law.", "hi-IN-SwaraNeural").save(audio_path))

print(f"Uploading files: img={img_path}, audio={audio_path}...")

with open(img_path, "rb") as f:
    up_img = requests.post(f"{url}/upload", files={"files": (os.path.basename(img_path), f, "image/png")}).json()[0]

with open(audio_path, "rb") as f:
    up_audio = requests.post(f"{url}/upload", files={"files": (os.path.basename(audio_path), f, "audio/mp3")}).json()[0]

img_obj = {"name": up_img, "data": None, "is_file": True}
audio_obj = {"name": up_audio, "data": None, "is_file": True}

print(f"Connecting to {ws_url} and waiting for queue processing...")
ws = websocket.create_connection(ws_url, timeout=120)

out_video_file = None

while True:
    try:
        res = ws.recv()
        if not res:
            break
        msg = json.loads(res)
        m_type = msg.get("msg")
        print("WS EVENT:", m_type)

        if m_type == "send_hash":
            ws.send(json.dumps({"fn_index": 0, "session_hash": session_hash}))

        elif m_type == "estimation":
            rank = msg.get("rank", 0)
            print(f"CURRENT QUEUE RANK: {rank}")

        elif m_type == "send_data":
            print("Sending inference payload...")
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

        elif m_type == "process_completed":
            out_data = msg.get("output", {}).get("data", [])
            print("PROCESS COMPLETED! OUT DATA:", out_data)
            if out_data and isinstance(out_data[0], dict):
                v_name = out_data[0].get("name")
                v_url = f"{url}/file={v_name}"
                print("Downloading generated talking video from:", v_url)
                vr = requests.get(v_url, timeout=30)
                out_video_file = "media_cache/real_talking_avatar.mp4"
                with open(out_video_file, "wb") as vf:
                    vf.write(vr.content)
                print(f"SUCCESSFULLY SAVED TALKING AVATAR VIDEO TO {out_video_file} (Size: {os.path.getsize(out_video_file)} bytes)!")
            break

    except Exception as e:
        print("WS EXCEPTION:", e)
        break

ws.close()
