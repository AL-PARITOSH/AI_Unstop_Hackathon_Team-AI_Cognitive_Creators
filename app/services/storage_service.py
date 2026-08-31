import os
import re
import hashlib
from typing import Optional
from app.config import settings

class StorageService:
    """
    Manages persistence of rendered HTML/SVG visual artifacts and generation of unique URLs.
    """

    @staticmethod
    def _slugify(text: str) -> str:
        s = re.sub(r'[^a-zA-Z0-9]+', '_', text.lower()).strip('_')
        return s[:30] if s else "visual"

    @staticmethod
    def generate_visual_id(concept: str, visual_type: str) -> str:
        slug = StorageService._slugify(concept)
        raw_hash = hashlib.md5(f"{concept}_{visual_type}".encode('utf-8')).hexdigest()[:6]
        return f"vis_{slug}_{visual_type}_{raw_hash}"

    @staticmethod
    def save_visual_artifact(visual_id: str, html_content: str) -> str:
        os.makedirs(settings.STATIC_DIR, exist_ok=True)
        filename = f"{visual_id}.html"
        filepath = os.path.join(settings.STATIC_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        return filename

    @staticmethod
    def get_visual_url(visual_id: str) -> str:
        base = settings.BASE_URL.rstrip('/')
        return f"{base}/visuals/{visual_id}.html"

    @staticmethod
    def read_visual_artifact(visual_id: str) -> Optional[str]:
        # Handle with or without .html suffix
        clean_id = visual_id.replace(".html", "")
        filename = f"{clean_id}.html"
        filepath = os.path.join(settings.STATIC_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return None
