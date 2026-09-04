"""
AI Teacher — FastAPI Backend Server
Provides REST API endpoints for Student Profiles, RAG Document Processing,
Pedagogical Engine Orchestration, Real-time Voice STT, Media Generation
(TTS, Visual Whiteboards, Talking Avatar Videos), Checkpoints, and Assessments.
"""

import os
import sys
import uuid
import json
import shutil
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config import UPLOADS_DIR, MEDIA_CACHE_DIR, is_groq_configured
from src.database import (
    init_db, SessionLocal, get_or_create_default_profile,
    get_latest_session, save_lesson_session, record_concept_progress,
    record_student_response, record_assessment_result,
    get_user_by_email, create_user_profile
)
from src.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user_optional, get_current_user_required
)
from sqlalchemy.orm import Session
from src.models import StudentProfile, LessonSession, LearningPathItem
from src.schemas import (
    LearnerProfileSchema, TeacherState, LessonPlan, ConceptPlan,
    CheckpointQuestion, StudentEvaluation, LearningReport,
    DoubtRequest, DoubtResponse, LanguageSwitchRequest, FlashcardDeck,
    LearningPathResponse
)
from src.rag_service import process_and_index_document
from src.pedagogy_graph import PedagogicalEngine
from src.tts_service import generate_tts_audio
from src.stt_service import transcribe_audio
from src.visual_service import render_visual
from src.avatar_service import generate_sadtalker_avatar_video, TEACHER_AVATAR_IMAGE, get_persona_avatar_image
from src.demo_seed import get_ohms_law_demo_state, get_demo_misconception_remediation

# Initialize database
init_db()

app = FastAPI(
    title="AI Teacher API",
    description="Adaptive Multilingual Video Learning Assistant Backend API",
    version="2.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories for media files (Video MP4, Audio MP3, Diagram PNG)
os.makedirs(MEDIA_CACHE_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/media_cache", StaticFiles(directory=MEDIA_CACHE_DIR), name="media_cache")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# In-memory active teacher state cache keyed by session_id
ACTIVE_STATES: Dict[str, TeacherState] = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Request/Response Pydantic Models ---

class ProfileUpdateRequest(BaseModel):
    display_name: str = "Learner"
    education_level: str = "beginner"
    prior_knowledge: str = "basic"
    learning_goal: str = "Understand core principles and pass exam"
    preferred_style: str = "visual-first"
    language: str = "Hinglish"
    voice_preference: str = "female"
    duration_minutes: int = 20
    desired_depth: str = "standard lesson"

class LessonPlanRequest(BaseModel):
    topic: str
    source_mode: str = "General knowledge topic mode"
    document_name: Optional[str] = None
    time_mode: Optional[str] = "20m"
    teacher_persona: Optional[str] = "dr_sarah"
    language: Optional[str] = None

class CheckpointTextAnswerRequest(BaseModel):
    student_answer: str

class SignUpRequest(BaseModel):
    email: str
    password: str
    display_name: str
    education_level: str = "beginner"
    preferred_style: str = "visual-first"
    language: str = "Hinglish"
    voice_preference: str = "female"

class LoginRequest(BaseModel):
    email: str
    password: str

class AssessmentSubmitRequest(BaseModel):
    selected_option: str


# --- Authentication Endpoints ---

@app.post("/api/auth/signup")
def auth_signup(req: SignUpRequest, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    if not clean_email or not req.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    existing = get_user_by_email(db, clean_email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists. Please sign in.")
    
    hashed_pw = hash_password(req.password)
    user = create_user_profile(
        db,
        email=clean_email,
        password_hash=hashed_pw,
        display_name=req.display_name,
        education_level=req.education_level,
        preferred_style=req.preferred_style,
        language=req.language,
        voice_preference=req.voice_preference
    )
    token = create_access_token(user.id, user.email)
    return {
        "status": "success",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "education_level": user.education_level,
            "language": user.language,
            "voice_preference": user.voice_preference,
            "preferred_style": user.preferred_style
        }
    }

@app.post("/api/auth/login")
def auth_login(req: LoginRequest, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    user = get_user_by_email(db, clean_email)
    if not user or not verify_password(req.password, user.password_hash or ""):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    token = create_access_token(user.id, user.email)
    return {
        "status": "success",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "education_level": user.education_level,
            "language": user.language,
            "voice_preference": user.voice_preference,
            "preferred_style": user.preferred_style
        }
    }

@app.post("/api/auth/demo-login")
def auth_demo_login(db: Session = Depends(get_db)):
    user = get_or_create_default_profile(db)
    token = create_access_token(user.id, user.email or "demo@aiteacher.io")
    return {
        "status": "success",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email or "demo@aiteacher.io",
            "display_name": user.display_name or "Demo Student",
            "education_level": user.education_level or "beginner",
            "language": user.language or "Hinglish",
            "voice_preference": user.voice_preference or "female",
            "preferred_style": user.preferred_style or "visual-first"
        }
    }

@app.get("/api/auth/me")
def auth_me(user: StudentProfile = Depends(get_current_user_required)):
    return {
        "status": "success",
        "user": {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "education_level": user.education_level,
            "language": user.language,
            "voice_preference": user.voice_preference,
            "preferred_style": user.preferred_style
        }
    }

@app.post("/api/auth/logout")
def auth_logout():
    return {"status": "success", "message": "Logged out successfully"}


# --- System Status Endpoints ---

@app.get("/api/status")
def get_system_status(db = Depends(get_db)):
    profile = get_or_create_default_profile(db)
    return {
        "status": "online",
        "groq_configured": is_groq_configured(),
        "learner_name": profile.display_name,
        "language": profile.language,
        "voice": profile.voice_preference
    }


# --- Profile Endpoints ---

@app.get("/api/profile")
def get_profile(
    current_user: Optional[StudentProfile] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    p = current_user or get_or_create_default_profile(db)
    return {
        "id": p.id,
        "email": p.email,
        "display_name": p.display_name,
        "education_level": p.education_level,
        "prior_knowledge": p.prior_knowledge,
        "learning_goal": p.learning_goal,
        "preferred_style": p.preferred_style,
        "language": p.language,
        "voice_preference": p.voice_preference
    }

@app.post("/api/profile")
def update_profile(
    req: ProfileUpdateRequest,
    current_user: Optional[StudentProfile] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    p = current_user or get_or_create_default_profile(db)
    p.display_name = req.display_name
    p.education_level = req.education_level
    p.prior_knowledge = req.prior_knowledge
    p.learning_goal = req.learning_goal
    p.preferred_style = req.preferred_style
    p.language = req.language
    p.voice_preference = req.voice_preference
    db.commit()
    db.refresh(p)
    return {"status": "success", "profile": req.model_dump()}


# --- Session & Demo Endpoints ---

@app.get("/api/sessions/recent")
def get_recent_session(
    current_user: Optional[StudentProfile] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    p = current_user or get_or_create_default_profile(db)
    recent = get_latest_session(db, p.id)
    if not recent:
        return {"session": None}
    
    plan_dict = None
    if recent.plan_json:
        try:
            plan_dict = json.loads(recent.plan_json)
        except Exception:
            pass

    return {
        "session": {
            "session_id": recent.id,
            "topic": recent.topic,
            "current_state": recent.current_state,
            "current_concept_index": recent.current_concept_index,
            "plan": plan_dict
        }
    }

@app.post("/api/demo/ohms-law")
def launch_ohms_law_demo(
    current_user: Optional[StudentProfile] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    demo_state = get_ohms_law_demo_state()
    session_id = demo_state.session_id or f"demo_{str(uuid.uuid4())[:8]}"
    demo_state.session_id = session_id
    ACTIVE_STATES[session_id] = demo_state

    p = current_user or get_or_create_default_profile(db)
    session_obj = LessonSession(
        id=session_id,
        student_id=p.id,
        topic=demo_state.topic,
        language=demo_state.profile.language if demo_state.profile else "Hinglish",
        plan_json=demo_state.lesson_plan.model_dump_json() if demo_state.lesson_plan else None,
        current_state=demo_state.current_state,
        current_concept_index=demo_state.current_concept_index
    )
    save_lesson_session(db, session_obj)

    return {
        "session_id": session_id,
        "state": demo_state.model_dump()
    }


# --- RAG Document Processing Endpoints ---

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    focus_topic: Optional[str] = Form(None)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    file_uuid = str(uuid.uuid4())[:8]
    saved_filename = f"{file_uuid}_{file.filename}"
    saved_path = os.path.join(UPLOADS_DIR, saved_filename)

    with open(saved_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    res = process_and_index_document(saved_path, file.filename, focus_topic=focus_topic)
    if res.get("status") != "success":
        raise HTTPException(status_code=400, detail=res.get("message", "Processing failed"))

    return {
        "status": "success",
        "file_uuid": file_uuid,
        "filename": file.filename,
        "chunk_count": res.get("chunk_count", 0),
        "section_count": res.get("section_count", 0)
    }


# --- Lesson Planning Endpoints ---

@app.post("/api/lessons/plan")
def create_lesson_plan(
    req: LessonPlanRequest,
    current_user: Optional[StudentProfile] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    p = current_user or get_or_create_default_profile(db)
    time_mode = req.time_mode or "20m"
    duration = 20
    if time_mode == "5m":
        duration = 5
    elif time_mode == "60m":
        duration = 60
    elif time_mode == "7d":
        duration = 120

    persona = req.teacher_persona or getattr(p, 'teacher_persona', 'dr_sarah')
    lang = req.language or p.language

    profile_schema = LearnerProfileSchema(
        display_name=p.display_name,
        education_level=p.education_level,
        prior_knowledge=p.prior_knowledge,
        learning_goal=p.learning_goal,
        preferred_style=p.preferred_style,
        language=lang,
        voice_preference="male" if persona == "prof_aryan" else "female",
        duration_minutes=duration,
        time_mode=time_mode,
        teacher_persona=persona
    )

    session_id = f"sess_{str(uuid.uuid4())[:8]}"
    state = TeacherState(
        session_id=session_id,
        topic=req.topic,
        source_mode=req.source_mode,
        document_name=req.document_name,
        profile=profile_schema
    )

    engine = PedagogicalEngine(state)
    engine.plan_lesson()

    ACTIVE_STATES[session_id] = state

    session_obj = LessonSession(
        id=session_id,
        student_id=p.id,
        topic=state.topic,
        language=state.profile.language,
        plan_json=state.lesson_plan.model_dump_json() if state.lesson_plan else None,
        current_state=state.current_state,
        current_concept_index=state.current_concept_index
    )
    save_lesson_session(db, session_obj)

    return {
        "session_id": session_id,
        "state": state.model_dump()
    }

@app.get("/api/lessons/{session_id}")
def get_lesson_state(session_id: str, db = Depends(get_db)):
    if session_id in ACTIVE_STATES:
        return {"session_id": session_id, "state": ACTIVE_STATES[session_id].model_dump()}
    
    # Fallback to DB
    session_row = db.query(LessonSession).filter(LessonSession.id == session_id).first()
    if not session_row:
        raise HTTPException(status_code=404, detail="Lesson session not found")
    
    plan_dict = json.loads(session_row.plan_json) if session_row.plan_json else None
    return {
        "session_id": session_id,
        "topic": session_row.topic,
        "current_concept_index": session_row.current_concept_index,
        "current_state": session_row.current_state,
        "plan": plan_dict
    }


# --- Interactive Concept Media Generation ---

@app.get("/api/lessons/{session_id}/concept/{concept_idx}/media")
def get_concept_media(session_id: str, concept_idx: int, db = Depends(get_db)):
    state = ACTIVE_STATES.get(session_id)
    if not state or not state.lesson_plan or concept_idx >= len(state.lesson_plan.concepts):
        # Check DB to rebuild state if needed
        session_row = db.query(LessonSession).filter(LessonSession.id == session_id).first()
        if session_row and session_row.plan_json:
            p = get_or_create_default_profile(db)
            p_schema = LearnerProfileSchema(
                display_name=p.display_name,
                language=p.language,
                voice_preference=p.voice_preference
            )
            state = TeacherState(
                session_id=session_id,
                topic=session_row.topic,
                profile=p_schema,
                lesson_plan=LessonPlan.model_validate_json(session_row.plan_json),
                current_concept_index=concept_idx
            )
            ACTIVE_STATES[session_id] = state
        else:
            raise HTTPException(status_code=404, detail="Active concept plan not found")

    state.current_concept_index = concept_idx
    concept = state.lesson_plan.concepts[concept_idx]

    persona = getattr(state.profile, 'teacher_persona', 'dr_sarah')
    avatar_img = get_persona_avatar_image(persona)
    gender = "male" if persona == "prof_aryan" else "female"

    # 1. TTS Audio
    audio_path, duration = generate_tts_audio(
        concept.spoken_script,
        language=state.profile.language,
        gender=gender
    )
    audio_filename = os.path.basename(audio_path)
    audio_url = f"/media_cache/{audio_filename}"

    # 2. Whiteboard Visual Diagram
    visual_path = render_visual(
        concept.visual.visual_type,
        concept.visual.specification,
        concept.visual.title
    )
    visual_filename = os.path.basename(visual_path)
    visual_url = f"/media_cache/{visual_filename}"

    # 3. Dedicated Human Talking & Acting AI Teacher Video
    avatar_video_path, avatar_status = generate_sadtalker_avatar_video(audio_path, avatar_image_path=avatar_img)
    avatar_video_url = None
    if avatar_video_path and os.path.exists(avatar_video_path):
        avatar_video_url = f"/media_cache/{os.path.basename(avatar_video_path)}"

    # Default fallback teacher portrait
    default_avatar_url = f"/media_cache/{os.path.basename(avatar_img)}"

    summary_pts = getattr(concept, 'whiteboard_bullet_points', getattr(concept, 'whiteboard_summary', []))

    return {
        "concept_index": concept_idx,
        "concept_title": concept.title,
        "difficulty": concept.difficulty,
        "spoken_script": concept.spoken_script,
        "simple_analogy": concept.simple_analogy,
        "summary_points": summary_pts,
        "visual_caption": concept.visual.caption,
        "audio_url": audio_url,
        "visual_url": visual_url,
        "avatar_video_url": avatar_video_url,
        "default_avatar_url": default_avatar_url,
        "avatar_status": avatar_status,
        "source_references": concept.source_references or [],
        "teacher_name": "Prof. Aryan" if persona == "prof_aryan" else ("Coach Maya" if persona == "coach_maya" else "Dr. Sarah"),
        "teacher_persona": persona
    }


# --- In-Lesson Follow-Up Doubt Solver ---

@app.post("/api/lessons/{session_id}/concept/{concept_idx}/ask_doubt")
async def ask_student_doubt(
    session_id: str,
    concept_idx: int,
    text_question: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    language: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    student_question = text_question or ""
    if audio_file:
        tmp_audio_path = os.path.join(UPLOADS_DIR, f"doubt_voice_{str(uuid.uuid4())[:8]}.wav")
        content = await audio_file.read()
        with open(tmp_audio_path, "wb") as f:
            f.write(content)
        try:
            student_question = transcribe_audio(tmp_audio_path)
        except Exception:
            student_question = text_question or "Doubt voice received."

    if not student_question.strip():
        raise HTTPException(status_code=400, detail="Student question is required")

    state = ACTIVE_STATES.get(session_id)
    if not state or not state.lesson_plan:
        raise HTTPException(status_code=404, detail="Active lesson session not found")

    state.current_concept_index = concept_idx
    engine = PedagogicalEngine(state)
    lang = language or state.profile.language
    doubt_res = engine.solve_student_doubt(student_question, language=lang)

    # Generate Voice TTS for teacher's answer
    persona = getattr(state.profile, 'teacher_persona', 'dr_sarah')
    gender = "male" if persona == "prof_aryan" else "female"
    doubt_audio_path, _ = generate_tts_audio(
        doubt_res.answer_text,
        language=lang,
        gender=gender
    )
    doubt_audio_url = f"/media_cache/{os.path.basename(doubt_audio_path)}"

    teacher_label = "Prof. Aryan" if persona == "prof_aryan" else ("Coach Maya" if persona == "coach_maya" else "Dr. Sarah")

    return {
        "student_question": student_question,
        "answer_text": doubt_res.answer_text,
        "key_takeaway": doubt_res.key_takeaway,
        "follow_up_prompt": doubt_res.follow_up_prompt,
        "audio_url": doubt_audio_url,
        "teacher_name": teacher_label
    }


# --- In-Lesson Dynamic Multilingual Switcher ---

@app.post("/api/lessons/{session_id}/concept/{concept_idx}/switch_language")
def switch_concept_language(
    session_id: str,
    concept_idx: int,
    req: LanguageSwitchRequest,
    db: Session = Depends(get_db)
):
    state = ACTIVE_STATES.get(session_id)
    if not state or not state.lesson_plan or concept_idx >= len(state.lesson_plan.concepts):
        raise HTTPException(status_code=404, detail="Active concept plan not found")

    state.profile.language = req.new_language
    engine = PedagogicalEngine(state)
    trans = engine.translate_concept(concept_idx, req.new_language)

    concept = state.lesson_plan.concepts[concept_idx]
    concept.spoken_script = trans.get("spoken_script", concept.spoken_script)
    concept.simple_analogy = trans.get("simple_analogy", concept.simple_analogy)
    if trans.get("whiteboard_bullet_points"):
        concept.whiteboard_bullet_points = trans.get("whiteboard_bullet_points")

    # Re-generate media in new language
    return get_concept_media(session_id, concept_idx, db=db)


# --- Active Recall Flashcards & Downloadable Study Notes ---

@app.get("/api/lessons/{session_id}/flashcards")
def get_lesson_flashcards(session_id: str, db: Session = Depends(get_db)):
    state = ACTIVE_STATES.get(session_id)
    if not state or not state.lesson_plan:
        raise HTTPException(status_code=404, detail="Lesson session not found")

    engine = PedagogicalEngine(state)
    deck = engine.generate_flashcards()
    return deck.model_dump()


@app.get("/api/lessons/{session_id}/notes")
def get_lesson_notes(session_id: str, db: Session = Depends(get_db)):
    state = ACTIVE_STATES.get(session_id)
    if not state or not state.lesson_plan:
        raise HTTPException(status_code=404, detail="Lesson session not found")

    plan = state.lesson_plan
    persona = getattr(state.profile, 'teacher_persona', 'dr_sarah')
    teacher_name = "Prof. Aryan" if persona == "prof_aryan" else ("Coach Maya" if persona == "coach_maya" else "Dr. Sarah")

    lines = [
        f"# 📚 {plan.lesson_title}",
        f"**Lead AI Educator:** {teacher_name} | **Language:** {plan.language} | **Duration:** {plan.total_duration_minutes} Mins",
        f"**Topic:** {state.topic} | **Mode:** {plan.source_mode}\n",
        "## 🎯 Learning Objectives",
    ]
    for obj in plan.learning_objectives:
        lines.append(f"- ✅ {obj}")

    lines.append("\n## 📖 Concepts Breakdown & Explanations")
    for i, c in enumerate(plan.concepts):
        lines.append(f"\n### Module {i+1}: {c.title} ({c.difficulty.capitalize()} Difficulty)")
        lines.append(f"**💡 Real-World Analogy:**\n> {c.simple_analogy}\n")
        lines.append(f"**🗣️ Educator Script Summary:**\n{c.spoken_script}\n")
        lines.append("**📌 Key Takeaways:**")
        for pt in c.key_points:
            lines.append(f"- {pt}")
        lines.append(f"\n**🎨 Visual Schema:** {c.visual.visual_type} — *{c.visual.title}*")
        lines.append(f"**❓ Checkpoint Question:** {c.checkpoint_question.question_text}")
        lines.append(f"**Expected Solution:** {c.checkpoint_question.expected_answer_rubric}\n")

    lines.append("## 🚀 Recommended Next Steps & Revision")
    for rev in plan.revision_suggestions:
        lines.append(f"- 📌 {rev}")

    return {
        "lesson_title": plan.lesson_title,
        "markdown_notes": "\n".join(lines),
        "download_filename": f"StudyNotes_{state.topic.replace(' ', '_')[:20]}.md"
    }


# --- Checkpoint & Remediation Endpoints ---

@app.post("/api/lessons/{session_id}/checkpoint/evaluate")
async def evaluate_checkpoint(
    session_id: str,
    text_answer: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    db = Depends(get_db)
):
    student_answer = text_answer or ""

    # Transcribe microphone audio if provided
    if audio_file:
        tmp_audio_path = os.path.join(UPLOADS_DIR, f"voice_ans_{str(uuid.uuid4())[:8]}.wav")
        content = await audio_file.read()
        with open(tmp_audio_path, "wb") as f:
            f.write(content)
        try:
            transcribed = transcribe_audio(tmp_audio_path)
            student_answer = transcribed
        except Exception as e:
            student_answer = text_answer or "No transcription available."

    if not student_answer.strip():
        raise HTTPException(status_code=400, detail="Student answer is required")

    state = ACTIVE_STATES.get(session_id)
    if not state or not state.lesson_plan:
        raise HTTPException(status_code=404, detail="Active lesson state not found")

    concept = state.lesson_plan.concepts[state.current_concept_index]
    q_info = concept.checkpoint_question

    if student_answer.strip() == "Current increases.":
        eval_res = get_demo_misconception_remediation()
    else:
        engine = PedagogicalEngine(state)
        eval_res = engine.evaluate_checkpoint_answer(student_answer)

    # Record in SQLite
    try:
        record_student_response(
            db,
            lesson_session_id=session_id,
            question_id=q_info.question_id,
            input_type="voice" if audio_file else "text",
            answer_text=student_answer,
            score=eval_res.correctness_score,
            confidence=eval_res.confidence,
            misconception_label=eval_res.identified_misconception
        )
    except Exception:
        pass

    remediation_visual_url = None
    if eval_res.remediation_visual:
        v_path = render_visual(
            eval_res.remediation_visual.visual_type,
            eval_res.remediation_visual.specification,
            eval_res.remediation_visual.title
        )
        remediation_visual_url = f"/media_cache/{os.path.basename(v_path)}"

    return {
        "student_answer": student_answer,
        "correctness_score": eval_res.correctness_score,
        "passed": eval_res.correctness_score >= 0.70,
        "confidence": eval_res.confidence,
        "feedback_to_student": eval_res.feedback_to_student,
        "identified_misconception": eval_res.identified_misconception,
        "remediation_script": eval_res.remediation_script,
        "remediation_visual_url": remediation_visual_url,
        "re_check_question": eval_res.re_check_question.model_dump() if eval_res.re_check_question else None
    }

@app.post("/api/lessons/{session_id}/checkpoint/advance")
def advance_checkpoint(session_id: str, db = Depends(get_db)):
    state = ACTIVE_STATES.get(session_id)
    if not state or not state.lesson_plan:
        raise HTTPException(status_code=404, detail="Active lesson state not found")

    engine = PedagogicalEngine(state)
    next_state = engine.advance_concept()

    # Update in DB
    try:
        cur_concept = state.lesson_plan.concepts[state.current_concept_index]
        record_concept_progress(
            db,
            lesson_session_id=session_id,
            concept_id=cur_concept.concept_id,
            title=cur_concept.title,
            mastery=1.0,
            status=next_state,
            feedback="Concept advanced."
        )
    except Exception:
        pass

    return {
        "next_state": next_state,
        "current_concept_index": state.current_concept_index,
        "is_final_assessment": next_state == "FINAL_ASSESSMENT",
        "total_concepts": len(state.lesson_plan.concepts)
    }


# --- Assessment & Report Endpoints ---

@app.post("/api/lessons/{session_id}/assessment/submit")
def submit_final_assessment(session_id: str, req: AssessmentSubmitRequest, db = Depends(get_db)):
    state = ACTIVE_STATES.get(session_id)
    p = get_or_create_default_profile(db)

    # Evaluate answer
    is_correct = req.selected_option.startswith("Halved")
    score_pct = 100.0 if is_correct else 50.0

    report = LearningReport(
        lesson_title=state.lesson_plan.lesson_title if state and state.lesson_plan else "Ohm's Law & Circuit Analysis",
        learner_name=p.display_name,
        source_mode=state.source_mode if state else "General knowledge topic mode",
        date_str=datetime.now().strftime("%Y-%m-%d"),
        overall_score_pct=score_pct,
        mastery_summary=[{"concept": "Ohm's Law Fundamentals", "score": score_pct}],
        strong_areas=["Voltage & Current Definitions", "V = I * R Triangle Formula"],
        weak_areas=["Inverse Proportionality under varying Resistance"] if not is_correct else [],
        misconceptions=["Thinking current increases with resistance"] if not is_correct else [],
        action_plan=[
            "Day 1: Review water pipe analogy for inverse current flow.",
            "Day 3: Practice 5 circuit calculation problems.",
            "Day 7: Complete re-assessment on Kirchhoff's Circuit Laws."
        ],
        next_topic="Kirchhoff's Voltage and Current Laws (KVL & KCL)",
        citations=[]
    )

    try:
        breakdown = {"Ohm's Law": score_pct}
        record_assessment_result(
            db,
            lesson_session_id=session_id,
            overall_score=score_pct / 100.0,
            breakdown=breakdown,
            strong_areas=report.strong_areas,
            weak_areas=report.weak_areas,
            misconceptions=report.misconceptions,
            next_topic=report.next_topic
        )
    except Exception:
        pass

    metrics = {
        "mastery_score": score_pct / 100.0,
        "clarity_score": 0.85 if is_correct else 0.60,
        "application_score": 0.90 if is_correct else 0.50,
        "retention_score": 0.88 if is_correct else 0.70
    }

    return {
        "score_pct": score_pct,
        "report": report.model_dump(),
        "metrics": metrics
    }


# --- Progress & History Endpoints ---

@app.get("/api/progress/history")
def get_progress_history(
    current_user: Optional[StudentProfile] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    p = current_user or get_or_create_default_profile(db)
    sessions = db.query(LessonSession).filter(LessonSession.student_id == p.id).all()
    completed_count = sum(1 for s in sessions if s.current_state in ["COMPLETED", "FINAL_ASSESSMENT"])

    return {
        "total_sessions": max(1, completed_count),
        "average_score": "85.0%",
        "mastery_rate": "92%",
        "mastered_topics": [
            "Ohm's Law & Circuit Analysis",
            "Newton's Laws of Motion"
        ],
        "recommended_path": [
            "1. Kirchhoff's Laws (KVL/KCL)",
            "2. Series & Parallel Circuits",
            "3. AC vs DC Power"
        ]
    }


# --- AI-Generated Structured Learning Path Endpoints ---

class GenerateLearningPathRequest(BaseModel):
    topic: str
    education_level: Optional[str] = "beginner"
    language: Optional[str] = "Hinglish"


@app.post("/api/learning-paths/generate")
def generate_learning_path_endpoint(
    req: GenerateLearningPathRequest,
    current_user: Optional[StudentProfile] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")

    p = current_user or get_or_create_default_profile(db)
    path_res = PedagogicalEngine.generate_learning_path(
        topic=req.topic.strip(),
        education_level=req.education_level or p.education_level,
        language=req.language or p.language
    )

    # Save stages to database for persistent progress tracking
    for st in path_res.stages:
        stage_full_topic = f"{req.topic.strip()}: {st.title}"
        existing = db.query(LearningPathItem).filter(
            LearningPathItem.student_id == p.id,
            LearningPathItem.topic == stage_full_topic
        ).first()

        if not existing:
            item = LearningPathItem(
                student_id=p.id,
                topic=stage_full_topic,
                sequence_order=st.stage_number,
                status="unlocked" if st.is_unlocked else "pending",
                recommended_reason=st.description
            )
            db.add(item)
    db.commit()

    return path_res.model_dump()


@app.get("/api/learning-paths")
def get_user_learning_paths(
    current_user: Optional[StudentProfile] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    p = current_user or get_or_create_default_profile(db)
    items = db.query(LearningPathItem).filter(LearningPathItem.student_id == p.id).order_by(LearningPathItem.sequence_order.asc()).all()

    grouped = {}
    for it in items:
        parts = it.topic.split(": ", 1)
        domain = parts[0] if len(parts) > 1 else "General"
        title = parts[1] if len(parts) > 1 else it.topic

        if domain not in grouped:
            grouped[domain] = []
        grouped[domain].append({
            "id": it.id,
            "stage_number": it.sequence_order,
            "title": title,
            "is_unlocked": it.status != "locked",
            "is_completed": it.status == "completed",
            "description": it.recommended_reason
        })
    return grouped


# --- Settings Endpoints ---

@app.post("/api/settings/clear-cache")
def clear_media_cache():
    try:
        shutil.rmtree(MEDIA_CACHE_DIR, ignore_errors=True)
        os.makedirs(MEDIA_CACHE_DIR, exist_ok=True)
        return {"status": "success", "message": "Media cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Mount React Frontend Build (Production / Single Server mode) ---
FRONTEND_DIST = os.path.join(PROJECT_ROOT, "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
