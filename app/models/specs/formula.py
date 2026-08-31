from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.specs.base import BaseVisualSpec

class FormulaVariable(BaseModel):
    symbol: str
    name: str
    unit: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None

class FormulaStep(BaseModel):
    step_number: int
    title: str
    latex_expression: str
    explanation: str

class FormulaSpec(BaseVisualSpec):
    visual_type: str = "formula"
    latex: str
    display_latex: Optional[str] = None
    variables: List[FormulaVariable] = Field(default_factory=list)
    derivation_steps: List[FormulaStep] = Field(default_factory=list)
    example_calculation: Optional[str] = None
    notes: Optional[str] = None
