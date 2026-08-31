import pytest
from app.models.request import VisualRequest
from app.generators.registry import SpecGeneratorRegistry
from app.renderers.registry import RendererRegistry

def test_all_renderers_output_validity():
    test_cases = [
        ("Physics", "Newton's Second Law", "formula"),
        ("Physics", "Ohm's Law", "diagram"),
        ("Biology", "Photosynthesis", "diagram"),
        ("Biology", "Photosynthesis", "flowchart"),
        ("Computer Science", "Binary Search", "flowchart"),
        ("Computer Science", "Binary Search", "code_execution"),
        ("Computer Science", "Python for loop", "code_execution"),
        ("Machine Learning", "Machine Learning pipeline", "architecture"),
        ("History", "French Revolution timeline", "timeline"),
        ("Mathematics", "y = x?", "graph")
    ]

    for topic, concept, vtype in test_cases:
        req = VisualRequest(topic=topic, concept=concept)
        spec = SpecGeneratorRegistry.generate(req, vtype)
        rendered = RendererRegistry.render(spec)

        assert rendered.format in ["svg", "katex", "plotly", "html"]
        assert rendered.full_html_page is not None
        assert len(rendered.full_html_page) > 100
        assert "<!DOCTYPE html>" in rendered.full_html_page

        if rendered.format == "svg":
            assert "<svg" in rendered.raw_svg
        elif rendered.format == "katex":
            assert rendered.latex_str is not None
        elif rendered.format == "plotly":
            assert rendered.plotly_dict is not None
        elif rendered.format == "html":
            assert rendered.raw_html is not None
