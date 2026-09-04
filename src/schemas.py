"""
Pydantic Schemas for Structured Output Parsing and LangGraph State.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class LearnerProfileSchema(BaseModel):
    display_name: str = Field(default="Learner", description="Student's name")
    education_level: str = Field(default="beginner", description="Class level, beginner, college, etc.")
    prior_knowledge: str = Field(default="basic", description="none, basic, moderate, strong")
    learning_goal: str = Field(default="Understand key concepts", description="Objective of learning")
    preferred_style: str = Field(default="visual-first", description="analogy-first, visual-first, step-by-step")
    language: str = Field(default="Hinglish", description="English, Hindi, Hinglish")
    voice_preference: str = Field(default="female", description="male, female")
    accessibility_preferences: str = Field(default="captions", description="accessibility settings")
    duration_minutes: int = Field(default=20, description="Available study time in minutes")
    time_mode: str = Field(default="20m", description="5m (speed blitz), 20m (standard), 60m (masterclass), 7d (7-day roadmap)")
    teacher_persona: str = Field(default="dr_sarah", description="dr_sarah (intuitive), prof_aryan (analytical), coach_maya (energetic)")
    desired_depth: str = Field(default="standard lesson", description="quick overview, standard lesson, deep lesson")


class SourceReference(BaseModel):
    document_name: str = Field(..., description="Name of uploaded source document")
    source_type: str = Field(..., description="pdf, docx, pptx, txt, md")
    page_number: Optional[int] = Field(None, description="Page number if PDF/DOCX")
    slide_number: Optional[int] = Field(None, description="Slide number if PPTX")
    section_heading: Optional[str] = Field(None, description="Heading or title of section")
    citation_text: str = Field(..., description="Exact snippet from source document")


class VisualSpec(BaseModel):
    visual_type: str = Field(..., description="diagram, illustration, formula, code, timeline, graph, concept_map, comparison_table")
    title: str = Field(..., description="Title for visual panel")
    specification: str = Field(..., description="Mermaid string, Python/Matplotlib code snippet, LaTeX formula, or image prompt")
    caption: str = Field(..., description="Short explanation of visual")


class CheckpointQuestion(BaseModel):
    question_id: str = Field(..., description="Unique question identifier")
    question_type: str = Field(..., description="mcq, short_answer, conceptual, reasoning")
    question_text: str = Field(..., description="The question asked to student")
    options: Optional[List[str]] = Field(None, description="Options if MCQ")
    correct_option_index: Optional[int] = Field(None, description="Index of correct option if MCQ")
    expected_answer_rubric: str = Field(..., description="Key points required in student answer")
    common_misconceptions: List[str] = Field(default_factory=list, description="Known common wrong ideas")


class ConceptPlan(BaseModel):
    concept_id: str = Field(..., description="Unique ID for concept e.g. concept_1")
    title: str = Field(..., description="Title of concept")
    prerequisite_ids: List[str] = Field(default_factory=list, description="IDs of prerequisite concepts")
    estimated_minutes: int = Field(default=5, description="Time budget in minutes")
    difficulty: str = Field(default="medium", description="easy, medium, hard")
    spoken_script: str = Field(..., description="Natural teaching spoken script in target language")
    whiteboard_bullet_points: List[str] = Field(..., description="Key points for whiteboard")
    simple_analogy: str = Field(..., description="Real-world analogy to explain concept")
    worked_example: str = Field(..., description="Step-by-step concrete example")
    visual: VisualSpec = Field(..., description="Subject-aware visual specification")
    key_points: List[str] = Field(..., description="Takeaways")
    source_references: List[SourceReference] = Field(default_factory=list, description="Citations if document grounded")
    checkpoint_question: CheckpointQuestion = Field(..., description="Interactive question after explanation")
    remediation_strategies: List[str] = Field(default_factory=list, description="Alternate explanation techniques")


class LessonPlan(BaseModel):
    lesson_title: str = Field(..., description="Overall lesson title")
    learner_profile_summary: str = Field(..., description="Summary of target learner")
    source_mode: str = Field(..., description="General knowledge topic mode OR Document-grounded mode")
    language: str = Field(..., description="English, Hindi, Hinglish")
    total_duration_minutes: int = Field(..., description="Total allocated minutes")
    learning_objectives: List[str] = Field(..., description="List of learning goals")
    prerequisite_concepts: List[str] = Field(default_factory=list, description="Prerequisites")
    concepts: List[ConceptPlan] = Field(..., description="Ordered list of concepts")
    revision_suggestions: List[str] = Field(default_factory=list, description="Follow-up topics")
    time_mode: Optional[str] = Field(default="20m", description="5m, 20m, 60m, 7d")
    seven_day_schedule: Optional[List[Dict[str, Any]]] = Field(default=None, description="Day-by-day roadmap if 7d mode")


class StudentEvaluation(BaseModel):
    correctness_score: float = Field(..., ge=0.0, le=1.0, description="Score from 0.0 to 1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Evaluator confidence score")
    concept_mastery: str = Field(..., description="low, medium, high")
    identified_misconception: Optional[str] = Field(None, description="Label of misconception if student struggled")
    supporting_evidence: str = Field(..., description="Quote or analysis of student's answer")
    feedback_to_student: str = Field(..., description="Constructive supportive teacher feedback")
    recommended_action: str = Field(..., description="advance, reinforce, remediate, simplify")
    remediation_script: Optional[str] = Field(None, description="New explanation with alternative analogy if remediating")
    remediation_visual: Optional[VisualSpec] = Field(None, description="New visual if remediating")
    re_check_question: Optional[CheckpointQuestion] = Field(None, description="Follow-up question if remediating")


class AssessmentQuestion(BaseModel):
    id: str
    question_type: str # mcq, short_answer, reasoning
    question_text: str
    options: Optional[List[str]] = None
    correct_option_index: Optional[int] = None
    rubric: str
    concept_id: str


class AssessmentResultSchema(BaseModel):
    overall_score: float
    score_breakdown: Dict[str, float]
    strong_concepts: List[str]
    weak_concepts: List[str]
    misconceptions_detected: List[str]
    feedback_summary: str
    next_recommended_topic: str
    seven_day_plan: List[str]


class LearningReport(BaseModel):
    lesson_title: str
    learner_name: str
    source_mode: str
    date_str: str
    overall_score_pct: float
    mastery_summary: List[Dict[str, Any]]
    strong_areas: List[str]
    weak_areas: List[str]
    misconceptions: List[str]
    action_plan: List[str]
    next_topic: str
    citations: List[str]


# State Dictionary compatible with LangGraph and FastAPI/React
class TeacherState(BaseModel):
    topic: str
    source_mode: str # General knowledge topic mode OR Document-grounded mode
    profile: LearnerProfileSchema
    document_name: Optional[str] = None
    retrieved_context: Optional[str] = ""
    lesson_plan: Optional[LessonPlan] = None
    current_concept_index: int = 0
    current_state: str = "UNDERSTAND_AND_PLAN"
    student_answers: Dict[str, Any] = Field(default_factory=dict)
    concept_remediation_counts: Dict[str, int] = Field(default_factory=dict)
    concept_mastery: Dict[str, float] = Field(default_factory=dict)
    identified_misconceptions: List[str] = Field(default_factory=list)
    assessment_results: Optional[AssessmentResultSchema] = None
    session_id: Optional[str] = None


PedagogicalState = TeacherState


# --- In-Lesson Doubt & Follow-up Q&A ---
class DoubtRequest(BaseModel):
    question_text: str = Field(..., description="Student's in-lesson doubt or question")
    language: Optional[str] = Field(None, description="Preferred language for answer")


class DoubtResponse(BaseModel):
    answer_text: str = Field(..., description="Educator's direct answer with intuitive example")
    audio_url: Optional[str] = Field(None, description="TTS voice audio url")
    key_takeaway: str = Field(..., description="One-sentence key takeaway")
    follow_up_prompt: Optional[str] = Field(None, description="Proactive check-in question")


# --- In-Lesson Dynamic Language Switch ---
class LanguageSwitchRequest(BaseModel):
    new_language: str = Field(..., description="English, Hindi, Hinglish, etc.")


# --- Active Recall Flashcards ---
class Flashcard(BaseModel):
    id: str
    concept_id: str
    front_question: str
    back_explanation: str
    analogy_or_mnemonic: str
    difficulty: str


class FlashcardDeck(BaseModel):
    lesson_title: str
    topic: str
    flashcards: List[Flashcard]


# --- AI-Generated Structured Learning Path ---
class LearningPathStage(BaseModel):
    stage_number: int
    title: str
    description: str
    estimated_hours: float
    difficulty: str
    key_skills: List[str]
    prerequisites: List[str]
    is_unlocked: bool = False
    is_completed: bool = False


class LearningPathResponse(BaseModel):
    path_id: str
    topic: str
    target_audience: str
    total_stages: int
    total_hours: float
    stages: List[LearningPathStage]


