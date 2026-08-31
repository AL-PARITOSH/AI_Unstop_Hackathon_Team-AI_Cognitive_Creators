from typing import Dict
from app.renderers.base import BaseRenderer, RenderedOutput
from app.renderers.diagram_renderer import DiagramRenderer
from app.renderers.flowchart_renderer import FlowchartRenderer
from app.renderers.formula_renderer import FormulaRenderer
from app.renderers.graph_renderer import GraphRenderer
from app.renderers.timeline_renderer import TimelineRenderer
from app.renderers.code_renderer import CodeRenderer
from app.renderers.architecture_renderer import ArchitectureRenderer
from app.models.specs.base import BaseVisualSpec

class RendererRegistry:
    """Central registry that dispatches visual specifications to the matching renderer."""
    _renderers: Dict[str, BaseRenderer] = {
        "diagram": DiagramRenderer(),
        "flowchart": FlowchartRenderer(),
        "formula": FormulaRenderer(),
        "graph": GraphRenderer(),
        "timeline": TimelineRenderer(),
        "code_execution": CodeRenderer(),
        "architecture": ArchitectureRenderer()
    }

    @classmethod
    def get_renderer(cls, visual_type: str) -> BaseRenderer:
        return cls._renderers.get(visual_type, cls._renderers["diagram"])

    @classmethod
    def render(cls, spec: BaseVisualSpec) -> RenderedOutput:
        renderer = cls.get_renderer(spec.visual_type)
        return renderer.render(spec)
