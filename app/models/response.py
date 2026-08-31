from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SelectorMetadata(BaseModel):
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the visual type selection")
    reason: str = Field(..., description="Pedagogical and technical reasoning for the chosen visual type")
    suggested_visual_types: List[str] = Field(default_factory=list, description="Ranked list of suitable visual types")

class VisualItem(BaseModel):
    visual_type: str = Field(..., description="Visual type name (diagram, flowchart, graph, formula, timeline, code_execution, architecture)")
    title: str = Field(..., description="Title of the visual explanation")
    explanation: str = Field(..., description="Pedagogical explanation accompanying the visual")
    visual_data: Dict[str, Any] = Field(..., description="Structured visual data payload, including SVG, KaTeX HTML, Plotly JSON, or state traces")
    visual_url: Optional[str] = Field(default=None, description="Direct standalone URL to embed/view the rendered visual in iframe or webview")

class VisualResponse(BaseModel):
    visual_type: str = Field(..., description="Primary visual type selected")
    title: str = Field(..., description="Title of the visual explanation")
    explanation: str = Field(..., description="Pedagogical explanation of the concept")
    selector_metadata: Optional[SelectorMetadata] = Field(default=None, description="Metadata from visual selector engine")
    visual_data: Dict[str, Any] = Field(..., description="Primary structured visual specification data and rendered markup")
    visual_url: Optional[str] = Field(default=None, description="Direct standalone URL to view or embed the primary visual")
    secondary_visuals: List[VisualItem] = Field(default_factory=list, description="List of complementary secondary visuals (e.g. circuit diagram alongside formula)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "visual_type": "formula",
                "title": "Newton's Second Law of Motion",
                "explanation": "Force equals mass multiplied by acceleration (F = m ? a).",
                "selector_metadata": {
                    "confidence": 0.96,
                    "reason": "Concept matches classical physics formula with clear algebraic relations.",
                    "suggested_visual_types": ["formula", "diagram", "graph"]
                },
                "visual_data": {
                    "format": "katex",
                    "latex": "F = m \cdot a",
                    "variables": [
                        {"symbol": "F", "name": "Force", "unit": "Newtons (N)"},
                        {"symbol": "m", "name": "Mass", "unit": "Kilograms (kg)"},
                        {"symbol": "a", "name": "Acceleration", "unit": "m/s?"}
                    ],
                    "rendered_html": "<div class='katex-formula'>...</div>"
                },
                "visual_url": "http://127.0.0.1:8000/visuals/vis_newton_abc123.html",
                "secondary_visuals": []
            }
        }
    }
