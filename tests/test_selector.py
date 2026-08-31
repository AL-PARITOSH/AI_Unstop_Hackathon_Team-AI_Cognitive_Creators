import pytest
from app.models.request import VisualRequest
from app.selector.rule_selector import RuleBasedVisualSelector
from app.selector.llm_selector import LLMVisualSelector

@pytest.fixture
def selector():
    return RuleBasedVisualSelector()

def test_newtons_law_selection(selector):
    req = VisualRequest(topic="Physics", concept="Newton's Second Law", level="beginner")
    res = selector.select(req)
    assert res.primary_type == "formula"
    assert "diagram" in res.secondary_types
    assert res.confidence >= 0.9
    assert "formula" in res.suggested_visual_types

def test_ohms_law_selection(selector):
    req = VisualRequest(topic="Physics", concept="Ohm's Law", level="intermediate")
    res = selector.select(req)
    assert res.primary_type == "formula"
    assert "diagram" in res.secondary_types
    assert res.confidence >= 0.9

def test_photosynthesis_selection(selector):
    req = VisualRequest(topic="Biology", concept="Photosynthesis", level="beginner")
    res = selector.select(req)
    assert res.primary_type == "diagram"
    assert "flowchart" in res.secondary_types

def test_binary_search_selection(selector):
    req = VisualRequest(topic="Computer Science", concept="Binary Search", level="intermediate")
    res = selector.select(req)
    assert res.primary_type == "flowchart"
    assert "code_execution" in res.secondary_types

def test_python_loop_selection(selector):
    req = VisualRequest(topic="Computer Science", concept="Python for loop", level="beginner")
    res = selector.select(req)
    assert res.primary_type == "code_execution"
    assert "flowchart" in res.secondary_types

def test_ml_pipeline_selection(selector):
    req = VisualRequest(topic="Machine Learning", concept="Machine Learning pipeline", level="advanced")
    res = selector.select(req)
    assert res.primary_type == "architecture"
    assert "flowchart" in res.secondary_types

def test_french_revolution_selection(selector):
    req = VisualRequest(topic="History", concept="French Revolution timeline", level="beginner")
    res = selector.select(req)
    assert res.primary_type == "timeline"

def test_y_equals_x_squared_selection(selector):
    req = VisualRequest(topic="Mathematics", concept="y = x?", level="intermediate")
    res = selector.select(req)
    assert res.primary_type == "graph"
    assert "formula" in res.secondary_types

def test_explicit_override(selector):
    req = VisualRequest(topic="Physics", concept="Newton's Second Law", visual_type_override="diagram")
    res = selector.select(req)
    assert res.primary_type == "diagram"
    assert res.confidence == 1.0

def test_low_confidence_safe_fallback(selector):
    req = VisualRequest(topic="General", concept="An Unseen Mysterious Phenomenon", lesson_context="")
    res = selector.select(req)
    assert res.primary_type in ["diagram", "flowchart"]
    assert "fallback" in res.reason.lower() or "diagram" in res.reason.lower()

def test_llm_selector_stub():
    llm_sel = LLMVisualSelector()
    req = VisualRequest(topic="Physics", concept="Newton's Second Law")
    res = llm_sel.select(req)
    assert res.primary_type == "formula"
    assert res.confidence > 0
