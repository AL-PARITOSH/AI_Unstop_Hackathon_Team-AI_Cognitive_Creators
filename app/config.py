import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "AI-Teacher Visual Explanation Engine"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = ""
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    BASE_URL: str = os.getenv("VISUAL_ENGINE_BASE_URL", "http://127.0.0.1:8000")
    STATIC_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
    CONFIDENCE_THRESHOLD_SAFE_FALLBACK: float = 0.45

settings = Settings()
