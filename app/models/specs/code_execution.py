from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.specs.base import BaseVisualSpec

class ExecutionTraceStep(BaseModel):
    step_number: int
    line_number: int
    code_line: str
    explanation: str
    variables_state: Dict[str, Any] = Field(default_factory=dict)
    output_printed: Optional[str] = None

class CodeExecutionSpec(BaseVisualSpec):
    visual_type: str = "code_execution"
    language: str = "python"
    code: str
    highlighted_lines: List[int] = Field(default_factory=list)
    execution_trace: List[ExecutionTraceStep] = Field(default_factory=list)
    expected_output: Optional[str] = None
    key_takeaways: List[str] = Field(default_factory=list)
