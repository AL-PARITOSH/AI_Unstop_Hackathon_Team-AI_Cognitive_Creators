import pytest
from app.models.request import VisualRequest
from app.generators.registry import SpecGeneratorRegistry
from app.generators.dynamic_builder import DynamicSpecBuilder

def test_curriculum_kb_generators():
    # 1. Newton
    req = VisualRequest(topic="Physics", concept="Newton's Second Law")
    spec = SpecGeneratorRegistry.generate(req, "formula")
    assert spec.visual_type == "formula"
    assert "F = m" in spec.latex

    # 2. Ohm
    req = VisualRequest(topic="Physics", concept="Ohm's Law")
    spec = SpecGeneratorRegistry.generate(req, "formula")
    assert spec.visual_type == "formula"
    assert len(spec.variables) == 3

    # 3. Photosynthesis
    req = VisualRequest(topic="Biology", concept="Photosynthesis")
    spec = SpecGeneratorRegistry.generate(req, "diagram")
    assert spec.visual_type == "diagram"
    assert len(spec.elements) > 0

    # 4. Binary Search
    req = VisualRequest(topic="Computer Science", concept="Binary Search")
    spec = SpecGeneratorRegistry.generate(req, "flowchart")
    assert spec.visual_type == "flowchart"
    assert len(spec.nodes) > 0

    # 5. Python Loop
    req = VisualRequest(topic="Computer Science", concept="Python for loop")
    spec = SpecGeneratorRegistry.generate(req, "code_execution")
    assert spec.visual_type == "code_execution"
    assert len(spec.execution_trace) > 0

    # 6. ML Pipeline
    req = VisualRequest(topic="Machine Learning", concept="Machine Learning pipeline")
    spec = SpecGeneratorRegistry.generate(req, "architecture")
    assert spec.visual_type == "architecture"
    assert len(spec.layers) == 5

    # 7. French Revolution
    req = VisualRequest(topic="History", concept="French Revolution timeline")
    spec = SpecGeneratorRegistry.generate(req, "timeline")
    assert spec.visual_type == "timeline"
    assert len(spec.events) >= 7

    # 8. y = x^2
    req = VisualRequest(topic="Mathematics", concept="y = x?")
    spec = SpecGeneratorRegistry.generate(req, "graph")
    assert spec.visual_type == "graph"
    assert len(spec.series) > 0

def test_dynamic_generators_all_types():
    types = ["diagram", "flowchart", "formula", "graph", "timeline", "code_execution", "architecture"]
    req = VisualRequest(topic="Astrophysics", concept="Stellar Nucleosynthesis", level="intermediate")
    
    for vt in types:
        spec = DynamicSpecBuilder.build(req, vt)
        assert spec.visual_type == vt
        assert "Stellar Nucleosynthesis" in spec.title
