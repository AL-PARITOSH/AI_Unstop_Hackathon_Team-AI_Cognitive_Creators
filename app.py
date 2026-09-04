"""
AI Teacher — Adaptive Multilingual Video Learning Assistant
Main Streamlit Application File.
"""

import streamlit as st
import os
import uuid
import json
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="AI Teacher — Multilingual Video Assistant",
    page_icon="👩‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.config import UPLOADS_DIR, is_groq_configured
from src.database import (
    init_db, SessionLocal, get_or_create_default_profile,
    get_latest_session, save_lesson_session, record_concept_progress,
    record_student_response, record_assessment_result
)
from src.models import StudentProfile, LessonSession, SourceDocument
from src.schemas import (
    LearnerProfileSchema, TeacherState, LessonPlan, ConceptPlan,
    CheckpointQuestion, StudentEvaluation, LearningReport
)
from src.rag_service import process_and_index_document, query_rag_context
from src.pedagogy_graph import PedagogicalEngine
from src.tts_service import generate_tts_audio
from src.stt_service import transcribe_audio
from src.visual_service import render_visual
from src.compositor import compose_lesson_segment_video, check_ffmpeg_available
from src.avatar_service import generate_sadtalker_avatar_video
from src.demo_seed import get_ohms_law_demo_state, get_demo_misconception_remediation
from src.ui_components import (
    render_stepper_bar, render_system_status_card,
    render_concept_media_panel, render_report_view
)

# Initialize database tables on launch
init_db()

# Session State Initialization
if "db" not in st.session_state:
    st.session_state.db = SessionLocal()

db = st.session_state.db

if "student_profile" not in st.session_state:
    st.session_state.student_profile = get_or_create_default_profile(db)

profile = st.session_state.student_profile

if "teacher_state" not in st.session_state:
    p_schema = LearnerProfileSchema(
        display_name=profile.display_name,
        education_level=profile.education_level,
        prior_knowledge=profile.prior_knowledge,
        learning_goal=profile.learning_goal,
        preferred_style=profile.preferred_style,
        language=profile.language,
        voice_preference=profile.voice_preference
    )
    st.session_state.teacher_state = TeacherState(
        topic="Ohm's Law",
        source_mode="General knowledge topic mode",
        profile=p_schema
    )

state = st.session_state.teacher_state

# Radio Navigation options
NAV_OPTIONS = [
    "🏠 Home / Resume",
    "👤 Learner Profile",
    "📚 Source & Topic",
    "📋 Lesson Plan",
    "👩‍🏫 Interactive Lesson",
    "✍️ Checkpoints",
    "📊 Assessment & Report",
    "📈 Progress Dashboard",
    "⚙️ Settings & System"
]

# Handle pending programmatic navigation BEFORE widget instantiation
if "pending_nav" in st.session_state:
    st.session_state["nav_choice"] = st.session_state.pop("pending_nav")

if "nav_choice" not in st.session_state:
    st.session_state["nav_choice"] = NAV_OPTIONS[0]

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/teacher.png", width=70)
    st.title("AI Teacher")
    st.caption("Adaptive Multilingual Educator")

    # Mode Indicator
    if state.source_mode == "Document-grounded mode":
        st.success("📄 Mode: Document Grounded")
    else:
        st.info("🌐 Mode: General Topic")

    # Active Language
    st.caption(f"Active Language: **{state.profile.language}** | Voice: **{state.profile.voice_preference.capitalize()}**")

    st.divider()

    nav_choice = st.radio(
        "Navigation",
        NAV_OPTIONS,
        key="nav_choice"
    )

    st.divider()
    render_system_status_card()


# --- TAB 1: HOME / RESUME ---
if nav_choice.startswith("🏠 Home"):
    st.markdown("# 👩‍🏫 AI Teacher — Adaptive Multilingual Video Learning Assistant")
    st.markdown(
        """
        Welcome to your personal AI Educator! Antigravity AI Teacher generates personalized, voice-narrated, visual-rich lessons
        grounded in your uploaded study materials or any educational topic.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🚀 Start New Learning Session")
        st.write("Enter a topic or upload lecture slides, papers, or textbooks.")
        if st.button("✨ Create New Lesson", type="primary", use_container_width=True):
            st.session_state["pending_nav"] = "📚 Source & Topic"
            st.rerun()

        st.markdown("---")
        st.markdown("### ⚡ Instant Hackathon Demo Mode")
        st.write("Load pre-configured Ohm's Law interactive session with misconception detection test.")
        if st.button("⚡ Launch Ohm's Law Demo Scenario", use_container_width=True):
            st.session_state.teacher_state = get_ohms_law_demo_state()
            st.session_state["pending_nav"] = "👩‍🏫 Interactive Lesson"
            st.rerun()

    with col2:
        st.markdown("### 🔄 Resume Recent Session")
        recent_session = get_latest_session(db, profile.id)
        if recent_session:
            st.info(f"**Topic:** {recent_session.topic}\n**State:** `{recent_session.current_state}`")
            if st.button("▶️ Resume Last Session", use_container_width=True):
                if recent_session.plan_json:
                    try:
                        plan_dict = json.loads(recent_session.plan_json)
                        state.lesson_plan = LessonPlan.model_validate(plan_dict)
                        state.topic = recent_session.topic
                        state.current_concept_index = recent_session.current_concept_index
                        state.current_state = recent_session.current_state
                        st.session_state["pending_nav"] = "👩‍🏫 Interactive Lesson"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error restoring session: {e}")
        else:
            st.write("No active paused session found.")


# --- TAB 2: LEARNER PROFILE ---
elif nav_choice.startswith("👤 Learner"):
    render_stepper_bar("Profile")
    st.markdown("## 👤 Personalize Your Learning Experience")

    with st.form("profile_form"):
        d_name = st.text_input("Display Name", value=profile.display_name)
        ed_level = st.selectbox(
            "Education Level",
            ["beginner", "class_8", "class_10", "class_12", "college", "interview_prep"],
            index=0
        )
        prior_k = st.selectbox(
            "Prior Knowledge in Subject",
            ["none", "basic", "moderate", "strong"],
            index=1
        )
        goal = st.text_input("Primary Learning Goal", value=profile.learning_goal)
        style = st.selectbox(
            "Preferred Teaching Style",
            ["visual-first", "analogy-first", "step-by-step", "technical-deep"],
            index=0
        )
        lang = st.selectbox(
            "Teaching Language",
            ["Hinglish", "Hindi", "English"],
            index=0
        )
        voice = st.selectbox(
            "Teacher Voice Persona",
            ["female", "male"],
            index=0
        )
        dur = st.slider("Target Lesson Duration (Minutes)", 5, 60, 20, step=5)
        depth = st.radio("Desired Lesson Depth", ["quick overview", "standard lesson", "deep lesson"], index=1)

        submitted = st.form_submit_button("💾 Save Profile Preferences", type="primary")

        if submitted:
            profile.display_name = d_name
            profile.education_level = ed_level
            profile.prior_knowledge = prior_k
            profile.learning_goal = goal
            profile.preferred_style = style
            profile.language = lang
            profile.voice_preference = voice
            db.commit()

            # Update active teacher state profile
            state.profile.display_name = d_name
            state.profile.education_level = ed_level
            state.profile.prior_knowledge = prior_k
            state.profile.learning_goal = goal
            state.profile.preferred_style = style
            state.profile.language = lang
            state.profile.voice_preference = voice
            state.profile.duration_minutes = dur
            state.profile.desired_depth = depth

            st.success("Profile preferences saved successfully!")


# --- TAB 3: SOURCE & TOPIC ---
elif nav_choice.startswith("📚 Source"):
    render_stepper_bar("Source")
    st.markdown("## 📚 Choose Learning Source")

    mode_choice = st.radio("Select Entry Mode", ["Enter Topic Directly", "Upload Learning Material (PDF, DOCX, PPTX, TXT, MD)"])

    if mode_choice == "Enter Topic Directly":
        state.source_mode = "General knowledge topic mode"
        topic_input = st.text_input("Educational Topic", value="Newton's Laws of Motion")
        if st.button("🚀 Generate Lesson Plan", type="primary"):
            state.topic = topic_input
            with st.spinner("🧠 AI Pedagogical Engine generating lesson plan..."):
                engine = PedagogicalEngine(state)
                engine.plan_lesson()
            st.session_state["pending_nav"] = "📋 Lesson Plan"
            st.rerun()

    else:
        state.source_mode = "Document-grounded mode"
        uploaded_file = st.file_uploader("Upload Learning Material", type=["pdf", "docx", "pptx", "txt", "md"])
        topic_input = st.text_input("Specific Topic / Chapter Focus (Optional)", value="Summary of uploaded content")

        if uploaded_file and st.button("📥 Process & Index Document", type="primary"):
            with st.spinner("📄 Extracting text, creating semantic chunks, and building ChromaDB vector index..."):
                file_uuid = str(uuid.uuid4())[:8]
                file_ext = os.path.splitext(uploaded_file.name)[1]
                saved_filename = f"{file_uuid}_{uploaded_file.name}"
                saved_path = os.path.join(UPLOADS_DIR, saved_filename)

                with open(saved_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                res = process_and_index_document(saved_path, uploaded_file.name)

                if res["status"] == "success":
                    st.success(f"Successfully indexed document! Created {res['chunk_count']} chunks from {res['section_count']} sections.")
                    state.topic = topic_input if topic_input else uploaded_file.name
                    
                    with st.spinner("🧠 Generating document-grounded lesson plan..."):
                        engine = PedagogicalEngine(state)
                        engine.plan_lesson()
                    st.session_state["pending_nav"] = "📋 Lesson Plan"
                    st.rerun()
                else:
                    st.error(f"Document extraction error: {res['message']}")


# --- TAB 4: LESSON PLAN ---
elif nav_choice.startswith("📋 Lesson"):
    render_stepper_bar("Lesson Plan")
    st.markdown("## 📋 Personalized Curriculum & Lesson Plan")

    if not state.lesson_plan:
        st.warning("No lesson plan generated yet. Please enter a topic or upload document under 'Source & Topic'.")
    else:
        plan = state.lesson_plan
        st.markdown(f"### Title: {plan.lesson_title}")
        st.caption(f"Mode: **{plan.source_mode}** | Language: **{plan.language}** | Duration: **{plan.total_duration_minutes} minutes**")

        st.markdown("#### Learning Objectives:")
        for obj in plan.learning_objectives:
            st.markdown(f"- {obj}")

        st.divider()
        st.markdown("#### Concepts Timeline:")

        for idx, concept in enumerate(plan.concepts):
            with st.expander(f"Concept {idx + 1}: {concept.title} ({concept.estimated_minutes} mins)", expanded=(idx == 0)):
                st.write(f"**Difficulty:** {concept.difficulty.capitalize()}")
                st.write(f"**Analogy:** {concept.simple_analogy}")
                st.write(f"**Visual Type:** `{concept.visual.visual_type}` — *{concept.visual.title}*")
                st.write(f"**Checkpoint Question:** {concept.checkpoint_question.question_text}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶️ Start Interactive Lesson", type="primary", use_container_width=True):
                state.current_concept_index = 0
                state.current_state = "EXPLAIN"
                st.session_state["pending_nav"] = "👩‍🏫 Interactive Lesson"
                st.rerun()
        with c2:
            if st.button("🔄 Regenerate Plan", use_container_width=True):
                with st.spinner("Regenerating plan..."):
                    engine = PedagogicalEngine(state)
                    engine.plan_lesson()
                st.rerun()


# --- TAB 5: INTERACTIVE LESSON ---
elif nav_choice.startswith("👩‍🏫 Interactive"):
    render_stepper_bar("Learn")
    
    if not state.lesson_plan or not state.lesson_plan.concepts:
        st.warning("Please create a lesson plan first.")
    else:
        concept = state.lesson_plan.concepts[state.current_concept_index]

        # Generate media assets
        with st.spinner("🎬 Preparing AI Teacher Narration, Visual Whiteboard & Motion Avatar..."):
            audio_path, duration = generate_tts_audio(
                concept.spoken_script,
                language=state.profile.language,
                gender=state.profile.voice_preference
            )
            visual_path = render_visual(
                concept.visual.visual_type,
                concept.visual.specification,
                concept.visual.title
            )
            avatar_video_path, avatar_status = generate_sadtalker_avatar_video(
                audio_path
            )

        render_concept_media_panel(
            concept,
            audio_path,
            visual_path,
            avatar_video_path,
            concept.source_references
        )

        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔁 Repeat Explanation", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("💡 Simplify Analogy", use_container_width=True):
                st.info(f"Simplified Analogy: {concept.simple_analogy}")
        with col3:
            if st.button("✍️ Proceed to Checkpoint Question", type="primary", use_container_width=True):
                state.current_state = "CHECKPOINT"
                st.session_state["pending_nav"] = "✍️ Checkpoints"
                st.rerun()


# --- TAB 6: CHECKPOINTS & REMEDIATION ---
elif nav_choice.startswith("✍️ Checkpoints"):
    render_stepper_bar("Checkpoints")

    if not state.lesson_plan or not state.lesson_plan.concepts:
        st.warning("No active lesson found.")
    else:
        concept = state.lesson_plan.concepts[state.current_concept_index]
        q_info = concept.checkpoint_question

        st.markdown(f"## ✍️ Checkpoint Question: Concept {state.current_concept_index + 1}")
        st.markdown(f"### {q_info.question_text}")

        # Input choices: Typed Answer OR Voice Input
        input_tab1, input_tab2 = st.tabs(["💬 Typed Answer", "🎙️ Spoken Voice Answer"])

        student_answer = ""

        with input_tab1:
            typed_ans = st.text_area("Type your explanation:", key="typed_checkpoint_ans")
            if typed_ans:
                student_answer = typed_ans

        with input_tab2:
            st.info("Click recorder to record your answer using your microphone.")
            audio_data = st.audio_input("Record voice answer")
            if audio_data is not None:
                tmp_audio_path = os.path.join(UPLOADS_DIR, "temp_voice_answer.wav")
                with open(tmp_audio_path, "wb") as f:
                    f.write(audio_data.read())
                
                with st.spinner("🎙️ Transcribing voice answer via Groq Whisper..."):
                    try:
                        transcribed = transcribe_audio(tmp_audio_path)
                        st.success(f"Transcribed: *\"{transcribed}\"*")
                        student_answer = transcribed
                    except Exception as e:
                        st.error(f"STT Error: {e}")

        # Quick Hackathon Demo Filler Button
        if st.button("⚡ Test Incorrect Answer Misconception Scenario"):
            student_answer = "Current increases."

        if st.button("Submit Checkpoint Answer", type="primary") and student_answer:
            with st.spinner("🔍 AI Diagnostic Evaluator analyzing conceptual understanding..."):
                if student_answer == "Current increases.":
                    # Instant demo misconception evaluation path
                    eval_res = get_demo_misconception_remediation()
                else:
                    engine = PedagogicalEngine(state)
                    eval_res = engine.evaluate_checkpoint_answer(student_answer)

            # Store result in DB
            record_student_response(
                db,
                state.session_id or "demo_session",
                q_info.question_id,
                "text",
                student_answer,
                eval_res.correctness_score,
                eval_res.confidence,
                eval_res.identified_misconception
            )

            st.divider()

            if eval_res.correctness_score >= 0.75:
                st.balloons()
                st.success(f"🎉 Excellent! Score: {int(eval_res.correctness_score * 100)}%")
                st.write(eval_res.feedback_to_student)
                if st.button("➡️ Advance to Next Concept"):
                    engine = PedagogicalEngine(state)
                    next_state = engine.advance_concept()
                    if next_state == "FINAL_ASSESSMENT":
                        st.session_state["pending_nav"] = "📊 Assessment & Report"
                    else:
                        st.session_state["pending_nav"] = "👩‍🏫 Interactive Lesson"
                    st.rerun()

            elif eval_res.correctness_score >= 0.40:
                st.info(f"👍 Good Progress! Score: {int(eval_res.correctness_score * 100)}%")
                st.write(eval_res.feedback_to_student)
                if st.button("➡️ Continue"):
                    engine = PedagogicalEngine(state)
                    next_state = engine.advance_concept()
                    if next_state == "FINAL_ASSESSMENT":
                        st.session_state["pending_nav"] = "📊 Assessment & Report"
                    else:
                        st.session_state["pending_nav"] = "👩‍🏫 Interactive Lesson"
                    st.rerun()

            else:
                st.error(f"⚠️ Diagnostic Gap Detected! Score: {int(eval_res.correctness_score * 100)}%")
                st.markdown(f"**Identified Misconception:** *{eval_res.identified_misconception}*")
                st.write(eval_res.feedback_to_student)

                st.markdown("### 🔄 Adaptive Remediation Explanation")
                st.write(eval_res.remediation_script)

                if eval_res.remediation_visual:
                    v_path = render_visual(
                        eval_res.remediation_visual.visual_type,
                        eval_res.remediation_visual.specification,
                        eval_res.remediation_visual.title
                    )
                    st.image(v_path, caption=eval_res.remediation_visual.caption, width=500)

                if eval_res.re_check_question:
                    st.markdown("#### 🎯 Targeted Re-Check Question:")
                    st.write(eval_res.re_check_question.question_text)


# --- TAB 7: ASSESSMENT & REPORT ---
elif nav_choice.startswith("📊 Assessment"):
    render_stepper_bar("Assessment")
    st.markdown("## 📊 Final Comprehensive Assessment & Learning Report")

    if st.button("🚀 Generate Final Assessment Quiz", type="primary"):
        st.session_state.quiz_ready = True

    if st.session_state.get("quiz_ready"):
        st.markdown("### Quiz Question 1: Application Problem")
        ans1 = st.radio(
            "If Resistance R is doubled under constant Voltage V, the new Current I will be:",
            ["Doubled (2x)", "Halved (1/2x)", "Quadrupled (4x)", "Unchanged"]
        )

        if st.button("Submit Final Quiz"):
            score_pct = 100.0 if ans1.startswith("Halved") else 50.0

            rep = LearningReport(
                lesson_title=state.lesson_plan.lesson_title if state.lesson_plan else "Ohm's Law",
                learner_name=profile.display_name,
                source_mode=state.source_mode,
                date_str=datetime.now().strftime("%Y-%m-%d"),
                overall_score_pct=score_pct,
                mastery_summary=[{"concept": "Ohm's Law Fundamentals", "score": score_pct}],
                strong_areas=["Voltage & Current Definitions", "V = I * R Triangle Formula"],
                weak_areas=["Inverse Proportionality under varying Resistance"] if score_pct < 100 else [],
                misconceptions=["Thinking current increases with resistance"] if score_pct < 100 else [],
                action_plan=[
                    "Day 1: Review water pipe analogy for inverse current flow.",
                    "Day 3: Practice 5 circuit calculation problems.",
                    "Day 7: Complete re-assessment on Kirchhoff's Circuit Laws."
                ],
                next_topic="Kirchhoff's Voltage and Current Laws (KVL & KCL)",
                citations=[]
            )

            render_report_view(rep)


# --- TAB 8: PROGRESS DASHBOARD ---
elif nav_choice.startswith("📈 Progress"):
    render_stepper_bar("Report")
    st.markdown("## 📈 Student Learning Progress & History")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sessions Completed", "3")
    with col2:
        st.metric("Average Quiz Score", "85.0%")
    with col3:
        st.metric("Concept Mastery Rate", "92%")

    st.markdown("### 🏆 Mastered Topics")
    st.success("✅ Ohm's Law & Circuit Analysis")
    st.success("✅ Newton's Laws of Motion")

    st.markdown("### 🎯 Recommended Learning Path")
    st.info("1. Kirchhoff's Laws (KVL/KCL) → 2. Series & Parallel Circuits → 3. AC vs DC Power")


# --- TAB 9: SETTINGS & SYSTEM ---
elif nav_choice.startswith("⚙️ Settings"):
    st.markdown("## ⚙️ System Settings & Diagnostics")

    render_system_status_card()

    st.markdown("### 🧹 Cache & Media Management")
    if st.button("Clear Generated Media Cache"):
        import shutil
        from src.config import MEDIA_CACHE_DIR
        shutil.rmtree(MEDIA_CACHE_DIR, ignore_errors=True)
        os.makedirs(MEDIA_CACHE_DIR, exist_ok=True)
        st.success("Media cache cleared successfully!")
