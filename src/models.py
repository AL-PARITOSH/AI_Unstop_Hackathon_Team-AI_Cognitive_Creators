"""
SQLAlchemy Database Models for Persistent Pedagogical History.
"""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(150), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    display_name = Column(String(100), nullable=False, default="Learner")
    education_level = Column(String(50), nullable=False, default="beginner") # beginner, class_8, college, etc.
    prior_knowledge = Column(String(50), nullable=False, default="basic")
    learning_goal = Column(String(200), nullable=False, default="Understand concepts thoroughly")
    preferred_style = Column(String(50), nullable=False, default="visual-first") # analogy-first, visual-first, step-by-step
    language = Column(String(20), nullable=False, default="Hinglish") # English, Hindi, Hinglish
    voice_preference = Column(String(50), nullable=False, default="female") # male, female
    accessibility_preferences = Column(Text, nullable=True, default="captions")
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("LessonSession", back_populates="student", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPathItem", back_populates="student", cascade="all, delete-orphan")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("student_profiles.id"), nullable=True)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)
    source_type = Column(String(20), nullable=False) # pdf, docx, pptx, txt, md
    page_or_slide_count = Column(Integer, default=0)
    extraction_status = Column(String(50), default="processed") # processed, error, ocr_needed
    created_at = Column(DateTime, default=datetime.utcnow)


class LessonSession(Base):
    __tablename__ = "lesson_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("student_profiles.id"), nullable=False)
    source_document_id = Column(String(36), ForeignKey("source_documents.id"), nullable=True)
    topic = Column(String(255), nullable=False)
    language = Column(String(20), nullable=False, default="Hinglish")
    duration_target = Column(Integer, default=20) # in minutes
    depth = Column(String(50), default="standard lesson") # quick overview, standard lesson, deep lesson
    current_state = Column(String(50), default="UNDERSTAND_AND_PLAN")
    current_concept_index = Column(Integer, default=0)
    plan_json = Column(Text, nullable=True) # Full LessonPlan JSON
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("StudentProfile", back_populates="sessions")
    concept_progresses = relationship("LessonConceptProgress", back_populates="lesson_session", cascade="all, delete-orphan")
    responses = relationship("StudentResponse", back_populates="lesson_session", cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", back_populates="lesson_session", cascade="all, delete-orphan")


class LessonConceptProgress(Base):
    __tablename__ = "lesson_concept_progresses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    lesson_session_id = Column(String(36), ForeignKey("lesson_sessions.id"), nullable=False)
    concept_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    attempts = Column(Integer, default=0)
    mastery_score = Column(Float, default=0.0)
    status = Column(String(50), default="in_progress") # in_progress, mastered, needs_revision
    last_feedback = Column(Text, nullable=True)
    remediation_count = Column(Integer, default=0)

    lesson_session = relationship("LessonSession", back_populates="concept_progresses")


class StudentResponse(Base):
    __tablename__ = "student_responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    lesson_session_id = Column(String(36), ForeignKey("lesson_sessions.id"), nullable=False)
    question_id = Column(String(100), nullable=False)
    input_type = Column(String(20), default="text") # text, voice
    answer_text = Column(Text, nullable=False)
    transcript_text = Column(Text, nullable=True)
    score = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    misconception_label = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lesson_session = relationship("LessonSession", back_populates="responses")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    lesson_session_id = Column(String(36), ForeignKey("lesson_sessions.id"), nullable=False)
    overall_score = Column(Float, default=0.0)
    score_breakdown_json = Column(Text, nullable=True)
    strong_areas_json = Column(Text, nullable=True)
    weak_areas_json = Column(Text, nullable=True)
    misconceptions_json = Column(Text, nullable=True)
    next_topic = Column(String(255), nullable=True)
    report_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lesson_session = relationship("LessonSession", back_populates="assessment_results")


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("student_profiles.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    sequence_order = Column(Integer, default=1)
    status = Column(String(50), default="pending") # pending, active, completed
    recommended_reason = Column(Text, nullable=True)

    student = relationship("StudentProfile", back_populates="learning_paths")
