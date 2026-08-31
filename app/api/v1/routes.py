from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from app.models.request import VisualRequest
from app.models.response import VisualResponse
from app.services.engine_service import VisualEngineService
from app.selector.taxonomy import SUPPORTED_VISUAL_TYPES
from app.selector.rule_selector import RuleBasedVisualSelector

router = APIRouter()
engine_service = VisualEngineService()
rule_selector = RuleBasedVisualSelector()

@router.post("/generate-visual", response_model=VisualResponse, summary="Generate Visual Explanation", description="Analyzes a lesson topic/concept, selects the optimal visual representation type, generates structured specifications, and renders ready-to-display visual outputs.")
def generate_visual_endpoint(request: VisualRequest) -> VisualResponse:
    try:
        return engine_service.generate_visual(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual generation error: {str(e)}")

@router.post("/select-type", summary="Preview Visual Selector Recommendation", description="Inspects which visual representation type would be selected for a given concept without generating full rendered artifacts.")
def select_visual_type_endpoint(request: VisualRequest) -> Dict[str, Any]:
    res = rule_selector.select(request)
    return {
        "concept": request.concept,
        "topic": request.topic,
        "primary_type": res.primary_type,
        "secondary_types": res.secondary_types,
        "confidence": res.confidence,
        "reason": res.reason,
        "suggested_visual_types": res.suggested_visual_types
    }

@router.get("/visual-types", summary="List Supported Visual Types", description="Lists all supported visual explanation types along with descriptions and render formats.")
def list_visual_types_endpoint() -> Dict[str, Any]:
    types_meta = {
        "formula": {"description": "LaTeX mathematical formulas with KaTeX HTML, variable breakdowns, and derivations", "format": "katex"},
        "diagram": {"description": "Vector anatomical, physical, and process diagrams with callouts and badges", "format": "svg"},
        "flowchart": {"description": "Algorithmic decision trees, control flow loops, and procedural sequences", "format": "svg"},
        "graph": {"description": "Plotly interactive Cartesian graphs, quadratic parabolas, curves, and data plots", "format": "plotly"},
        "timeline": {"description": "Chronological milestone trackers for historical and evolutionary concepts", "format": "svg"},
        "code_execution": {"description": "Syntax-highlighted source code with step-by-step memory trace state tables", "format": "html"},
        "architecture": {"description": "Multi-tier system architectures, ML pipelines, and data flow diagrams", "format": "svg"}
    }
    return {
        "supported_types": SUPPORTED_VISUAL_TYPES,
        "metadata": types_meta
    }

@router.get("/examples", summary="List Benchmark Examples", description="Returns standard curriculum benchmark examples ready for testing against the engine.")
def list_examples_endpoint() -> Dict[str, Any]:
    examples = [
        {"id": 1, "topic": "Physics", "concept": "Newton's Second Law", "level": "beginner", "expected_type": "formula", "secondary": "diagram"},
        {"id": 2, "topic": "Physics", "concept": "Ohm's Law", "level": "intermediate", "expected_type": "formula", "secondary": "diagram"},
        {"id": 3, "topic": "Biology", "concept": "Photosynthesis", "level": "beginner", "expected_type": "diagram", "secondary": "flowchart"},
        {"id": 4, "topic": "Computer Science", "concept": "Binary Search", "level": "intermediate", "expected_type": "flowchart", "secondary": "code_execution"},
        {"id": 5, "topic": "Computer Science", "concept": "Python for loop", "level": "beginner", "expected_type": "code_execution", "secondary": "flowchart"},
        {"id": 6, "topic": "Machine Learning", "concept": "Machine Learning pipeline", "level": "advanced", "expected_type": "architecture", "secondary": "flowchart"},
        {"id": 7, "topic": "History", "concept": "French Revolution timeline", "level": "beginner", "expected_type": "timeline", "secondary": "flowchart"},
        {"id": 8, "topic": "Mathematics", "concept": "y = x?", "level": "intermediate", "expected_type": "graph", "secondary": "formula"}
    ]
    return {
        "total_examples": len(examples),
        "examples": examples
    }

@router.get("/health", summary="Engine Health Check")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "AI-Teacher Visual Explanation Engine",
        "version": "1.0.0"
    }
