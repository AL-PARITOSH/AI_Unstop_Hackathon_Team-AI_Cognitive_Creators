from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.models.specs.base import BaseVisualSpec

class GraphSeries(BaseModel):
    name: str
    x_values: List[float] = Field(default_factory=list)
    y_values: List[float] = Field(default_factory=list)
    mode: Literal["lines", "markers", "lines+markers", "bar", "area"] = "lines"
    line_color: Optional[str] = None
    line_width: int = 3
    line_dash: Optional[str] = None

class GraphPointAnnotation(BaseModel):
    x: float
    y: float
    text: str
    point_color: str = "#EF4444"

class GraphSpec(BaseVisualSpec):
    visual_type: str = "graph"
    chart_type: Literal["line", "scatter", "bar", "function_plot"] = "function_plot"
    x_label: str = "x"
    y_label: str = "y"
    series: List[GraphSeries] = Field(default_factory=list)
    annotations: List[GraphPointAnnotation] = Field(default_factory=list)
    x_range: Optional[List[float]] = None
    y_range: Optional[List[float]] = None
    show_grid: bool = True
    plotly_layout_override: Dict[str, Any] = Field(default_factory=dict)
