from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel, Field
from app.models.request import VisualRequest

class SelectorResult(BaseModel):
    primary_type: str = Field(..., description="Selected primary visual type")
    secondary_types: List[str] = Field(default_factory=list, description="Complementary secondary visual types")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reason: str = Field(..., description="Explanation of why this visual type was selected")
    suggested_visual_types: List[str] = Field(default_factory=list, description="Ranked list of suitable visual types")

class BaseVisualSelector(ABC):
    @abstractmethod
    def select(self, request: VisualRequest) -> SelectorResult:
        """Determines the appropriate visual type(s) based on topic, concept, and context."""
        pass
