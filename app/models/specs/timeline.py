from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from app.models.specs.base import BaseVisualSpec

class TimelineEvent(BaseModel):
    date_or_period: str
    title: str
    description: str
    category: Optional[str] = None
    importance: Literal["high", "medium", "low"] = "medium"
    tags: List[str] = Field(default_factory=list)

class TimelineSpec(BaseVisualSpec):
    visual_type: str = "timeline"
    orientation: Literal["horizontal", "vertical"] = "horizontal"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    events: List[TimelineEvent] = Field(default_factory=list)
