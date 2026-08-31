from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from app.models.specs.base import BaseVisualSpec

class ArchLayer(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    color: str = "#3B82F6"

class ArchComponent(BaseModel):
    id: str
    name: str
    layer_id: str
    technology: Optional[str] = None
    role: str
    icon: Optional[str] = None

class ArchConnection(BaseModel):
    from_id: str
    to_id: str
    label: Optional[str] = None
    protocol_or_type: Literal["sync", "async", "stream", "pipeline", "data_flow"] = "pipeline"

class ArchitectureSpec(BaseVisualSpec):
    visual_type: str = "architecture"
    layers: List[ArchLayer] = Field(default_factory=list)
    components: List[ArchComponent] = Field(default_factory=list)
    connections: List[ArchConnection] = Field(default_factory=list)
    key_principles: List[str] = Field(default_factory=list)
