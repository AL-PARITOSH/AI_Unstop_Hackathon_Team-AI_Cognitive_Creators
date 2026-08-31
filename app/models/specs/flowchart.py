from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from app.models.specs.base import BaseVisualSpec

class FlowNode(BaseModel):
    id: str
    label: str
    node_type: Literal["start", "end", "process", "decision", "input_output", "loop"] = "process"
    detail: Optional[str] = None
    color: Optional[str] = None

class FlowEdge(BaseModel):
    source_id: str
    target_id: str
    label: Optional[str] = None
    condition: Optional[str] = None

class FlowchartSpec(BaseVisualSpec):
    visual_type: str = "flowchart"
    orientation: Literal["vertical", "horizontal"] = "vertical"
    nodes: List[FlowNode] = Field(default_factory=list)
    edges: List[FlowEdge] = Field(default_factory=list)
