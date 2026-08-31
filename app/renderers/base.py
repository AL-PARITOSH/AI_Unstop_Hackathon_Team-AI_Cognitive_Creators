from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.specs.base import BaseVisualSpec

class RenderedOutput(BaseModel):
    format: str = Field(..., description="Primary format: svg, katex, plotly, html")
    raw_svg: Optional[str] = Field(default=None, description="Raw SVG markup if applicable")
    raw_html: Optional[str] = Field(default=None, description="Inline embeddable HTML component")
    plotly_dict: Optional[Dict[str, Any]] = Field(default=None, description="Plotly figure JSON dict")
    latex_str: Optional[str] = Field(default=None, description="Raw LaTeX string")
    full_html_page: str = Field(..., description="Complete self-contained standalone HTML page for iframe or browser preview")

class BaseRenderer(ABC):
    @abstractmethod
    def render(self, spec: BaseVisualSpec) -> RenderedOutput:
        """Renders a visual specification into structured render artifacts and standalone HTML."""
        pass
