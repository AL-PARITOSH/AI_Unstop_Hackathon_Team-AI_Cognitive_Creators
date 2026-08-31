from typing import Optional, Literal
from pydantic import BaseModel, Field

class VisualRequest(BaseModel):
    topic: str = Field(..., description="Discipline or subject area (e.g. Physics, Computer Science, Biology, Mathematics, History)")
    concept: str = Field(..., description="Specific concept or lesson title (e.g. Newton's Second Law, Binary Search, Photosynthesis)")
    level: Literal["beginner", "intermediate", "advanced"] = Field(default="beginner", description="Target learner complexity level")
    language: str = Field(default="English", description="Explanation language")
    lesson_context: Optional[str] = Field(default=None, description="Context, dialogue, or lesson prompt from the AI Teacher")
    include_secondary: bool = Field(default=True, description="Whether to include complementary secondary visual specifications")
    visual_type_override: Optional[str] = Field(default=None, description="Optional manual visual type override (e.g. diagram, flowchart, graph, formula, timeline, code_execution, architecture)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "topic": "Physics",
                "concept": "Newton's Second Law",
                "level": "beginner",
                "language": "English",
                "lesson_context": "Explain the fundamental equation connecting force, mass, and acceleration.",
                "include_secondary": True
            }
        }
    }
