from typing import Dict, Any
from pydantic import BaseModel, Field

class BaseVisualSpec(BaseModel):
    title: str = Field(..., description="Title of the visual")
    explanation: str = Field(..., description="Educational explanation accompanying the visual")
    visual_type: str = Field(..., description="Visual type identifier")
    level: str = Field(default="beginner", description="Difficulty/depth level: beginner, intermediate, advanced")
    theme: str = Field(default="light", description="Visual theme: light or dark")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom generator or renderer metadata")
