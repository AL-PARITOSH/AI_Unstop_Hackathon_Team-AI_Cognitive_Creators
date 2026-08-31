from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from app.models.specs.base import BaseVisualSpec

class DiagramElement(BaseModel):
    id: str
    label: str
    subtext: Optional[str] = None
    shape: Literal["rect", "circle", "ellipse", "cylinder", "diamond", "box", "pill", "card"] = "rect"
    x: int
    y: int
    width: int
    height: int
    color: str = "#2563EB"
    bg_color: str = "#EFF6FF"
    border_color: str = "#3B82F6"
    icon: Optional[str] = None

class DiagramConnection(BaseModel):
    source_id: str
    target_id: str
    label: Optional[str] = None
    arrow_type: Literal["forward", "bidirectional", "dashed", "solid"] = "forward"
    color: str = "#64748B"

class DiagramAnnotation(BaseModel):
    title: str
    text: str
    x: int
    y: int
    color: str = "#10B981"

class DiagramSpec(BaseVisualSpec):
    visual_type: str = "diagram"
    canvas_width: int = 800
    canvas_height: int = 500
    elements: List[DiagramElement] = Field(default_factory=list)
    connections: List[DiagramConnection] = Field(default_factory=list)
    annotations: List[DiagramAnnotation] = Field(default_factory=list)
