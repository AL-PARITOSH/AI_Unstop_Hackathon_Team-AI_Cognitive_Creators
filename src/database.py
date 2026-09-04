"""
Database engine initialization and persistence helper functions.
"""

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from src.config import DATABASE_URL
from src.models import (
    Base, StudentProfile, SourceDocument, LessonSession,
    LessonConceptProgress, StudentResponse, AssessmentResult, LearningPathItem
)
import json

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create database tables if they do not exist and ensure new columns exist."""
    Base.metadata.create_all(bind=engine)
    
    # Safe SQLite column migrations for student_profiles
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            result = conn.execute(text("PRAGMA table_info(student_profiles)")).fetchall()
            col_names = [r[1] for r in result]
            
            if "email" not in col_names:
                conn.execute(text("ALTER TABLE student_profiles ADD COLUMN email VARCHAR(150)"))
            if "password_hash" not in col_names:
                conn.execute(text("ALTER TABLE student_profiles ADD COLUMN password_hash VARCHAR(255)"))
            if "avatar_url" not in col_names:
                conn.execute(text("ALTER TABLE student_profiles ADD COLUMN avatar_url VARCHAR(255)"))
            conn.commit()
        except Exception:
            pass

def get_db():
    """Session generator for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_email(db: Session, email: str):
    """Lookup student profile by unique email."""
    if not email:
        return None
    return db.query(StudentProfile).filter(StudentProfile.email == email.strip().lower()).first()

def create_user_profile(
    db: Session,
    email: str,
    password_hash: str,
    display_name: str,
    education_level: str = "beginner",
    preferred_style: str = "visual-first",
    language: str = "Hinglish",
    voice_preference: str = "female"
) -> StudentProfile:
    """Register a new student profile in SQLite."""
    user = StudentProfile(
        email=email.strip().lower(),
        password_hash=password_hash,
        display_name=display_name.strip() if display_name else "Student",
        education_level=education_level,
        preferred_style=preferred_style,
        language=language,
        voice_preference=voice_preference,
        learning_goal="Master core concepts through interactive visuals",
        accessibility_preferences="captions"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_or_create_default_profile(db: Session) -> StudentProfile:
    """Retrieve existing profile or create a default student profile."""
    profile = db.query(StudentProfile).filter(StudentProfile.email == "demo@aiteacher.io").first()
    if not profile:
        profile = db.query(StudentProfile).first()
    if not profile:
        profile = StudentProfile(
            email="demo@aiteacher.io",
            display_name="Demo Student",
            education_level="beginner",
            prior_knowledge="basic",
            learning_goal="Master core concepts through interactive visuals",
            preferred_style="visual-first",
            language="Hinglish",
            voice_preference="female",
            accessibility_preferences="captions"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

def get_latest_session(db: Session, student_id: str) -> LessonSession:
    """Get the most recent active or paused session for a student."""
    return db.query(LessonSession).filter(
        LessonSession.student_id == student_id,
        LessonSession.completed_at == None
    ).order_by(desc(LessonSession.started_at)).first()

def save_lesson_session(db: Session, session: LessonSession):
    """Save or update a lesson session."""
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def record_concept_progress(db: Session, lesson_session_id: str, concept_id: str, title: str, mastery: float, status: str, feedback: str, remediation_increment: bool = False):
    """Update or insert progress for a single concept in a session."""
    progress = db.query(LessonConceptProgress).filter(
        LessonConceptProgress.lesson_session_id == lesson_session_id,
        LessonConceptProgress.concept_id == concept_id
    ).first()
    if not progress:
        progress = LessonConceptProgress(
            lesson_session_id=lesson_session_id,
            concept_id=concept_id,
            title=title,
            attempts=1,
            mastery_score=mastery,
            status=status,
            last_feedback=feedback,
            remediation_count=1 if remediation_increment else 0
        )
        db.add(progress)
    else:
        progress.attempts += 1
        progress.mastery_score = mastery
        progress.status = status
        progress.last_feedback = feedback
        if remediation_increment:
            progress.remediation_count += 1
    db.commit()
    return progress

def record_student_response(db: Session, lesson_session_id: str, question_id: str, input_type: str, answer_text: str, score: float, confidence: float, misconception_label: str = None):
    """Save student question attempt."""
    resp = StudentResponse(
        lesson_session_id=lesson_session_id,
        question_id=question_id,
        input_type=input_type,
        answer_text=answer_text,
        score=score,
        confidence=confidence,
        misconception_label=misconception_label
    )
    db.add(resp)
    db.commit()
    return resp

def record_assessment_result(db: Session, lesson_session_id: str, overall_score: float, breakdown: dict, strong_areas: list, weak_areas: list, misconceptions: list, next_topic: str):
    """Save final evaluation report."""
    res = AssessmentResult(
        lesson_session_id=lesson_session_id,
        overall_score=overall_score,
        score_breakdown_json=json.dumps(breakdown),
        strong_areas_json=json.dumps(strong_areas),
        weak_areas_json=json.dumps(weak_areas),
        misconceptions_json=json.dumps(misconceptions),
        next_topic=next_topic
    )
    db.add(res)
    
    # Mark session as completed
    session = db.query(LessonSession).filter(LessonSession.id == lesson_session_id).first()
    if session:
        from datetime import datetime
        session.completed_at = datetime.utcnow()
        session.current_state = "COMPLETED"
        db.add(session)

    db.commit()
    return res
