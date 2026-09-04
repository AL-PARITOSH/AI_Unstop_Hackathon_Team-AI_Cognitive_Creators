"""
UI Components module for rendering metrics, lesson plans, media panels, and progress bars.
"""

import os
import streamlit as st
from src.schemas import PedagogicalState
from src.avatar_service import TEACHER_AVATAR_IMAGE

def render_stepper_bar(current_step: str):
    """Render top pedagogical progress stepper bar."""
    steps = ["Profile", "Source", "Lesson Plan", "Learn", "Checkpoints", "Assessment", "Report"]
    cols = st.columns(len(steps))
    for idx, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if step == current_step:
                st.button(f"🎯 {step}", key=f"step_{step}", use_container_width=True, type="primary")
            else:
                st.button(f"👤 {step}" if idx == 0 else f"📖 {step}", key=f"step_{step}", use_container_width=True, disabled=True)


def render_pedagogical_status_badge(state: PedagogicalState):
    """Render current pedagogical state pill and mastery progress bar."""
    if not state or not state.profile:
        return

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.caption(f"🎯 **Learner**: {state.profile.display_name} | 🌐 **Language**: {state.profile.language}")
    with col2:
        st.caption(f"🧠 **Stage**: `{state.current_state.upper()}` | 🔄 **Misconceptions**: {len(state.identified_misconceptions)}")
    with col3:
        mastery_pct = int(getattr(state, 'overall_mastery_score', 0.8) * 100)
        st.progress(getattr(state, 'overall_mastery_score', 0.8), text=f"Mastery: {mastery_pct}%")


def render_concept_card(concept, index: int, is_active: bool = False):
    """Render summary card for a single concept in lesson plan."""
    diff_level = getattr(concept, 'difficulty', getattr(concept, 'difficulty_level', 'medium'))
    target_obj = getattr(concept, 'target_objective', getattr(concept, 'title', 'Learn concept'))
    
    with st.container():
        st.markdown(f"#### Concept {index + 1}: {concept.title}")
        st.write(f"**Target Objective**: {target_obj}")
        st.caption(f"Estimated Time: {concept.estimated_minutes} mins | Difficulty: {diff_level}")
        st.info(f"💡 **Analogy**: {concept.simple_analogy}")


def render_concept_media_panel(concept, audio_path: str, visual_image_path: str, avatar_video_path: str = None, source_references: list = None):
    """
    Render teaching panel showing:
    - Left Column (60% width): Whiteboard Visual representation (Pollinations AI / Kroki / Matplotlib diagram)
    - Right Column (40% width): Human Talking & Acting AI Teacher Assistant Video Player
    """
    diff_level = getattr(concept, 'difficulty', getattr(concept, 'difficulty_level', 'medium'))
    summary_pts = getattr(concept, 'whiteboard_bullet_points', getattr(concept, 'whiteboard_summary', getattr(concept, 'key_points', [])))
    concept_id_str = concept.concept_id.replace('concept_', '') if hasattr(concept, 'concept_id') else ''

    st.markdown(f"### 📖 Concept {concept_id_str}: {concept.title}")

    col_left, col_right = st.columns([1.5, 1.0])

    # Left Side: Whiteboard Visual Representation
    with col_left:
        st.markdown("#### 🎨 Visual Representation")
        if visual_image_path and os.path.exists(visual_image_path):
            st.image(visual_image_path, use_container_width=True, caption=concept.visual.caption)
        else:
            st.info("Visual representation loading...")

    # Right Side: Dedicated Human Talking & Acting AI Teacher Assistant Video Player
    with col_right:
        st.markdown("#### 👩‍🏫 AI Teacher Assistant (Voice & Motion Act)")
        
        if avatar_video_path and os.path.exists(avatar_video_path) and os.path.getsize(avatar_video_path) > 1000:
            st.video(avatar_video_path)
        else:
            if os.path.exists(TEACHER_AVATAR_IMAGE):
                st.image(TEACHER_AVATAR_IMAGE, use_container_width=True)

            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                try:
                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()
                    audio_fmt = "audio/wav" if audio_path.endswith(".wav") else "audio/mp3"
                    st.audio(audio_bytes, format=audio_fmt)
                except Exception as e:
                    st.error(f"Audio playback error: {e}")

    # Spoken Script & Whiteboard Summary expander
    with st.expander("📄 View Spoken Script & Whiteboard Summary"):
        st.write(f"**Spoken Script ({diff_level} level)**:")
        st.write(concept.spoken_script)

        st.markdown("---")
        st.write("**Key Concept Bullet Points**:")
        for pt in summary_pts:
            st.markdown(f"- {pt}")

    if source_references:
        st.caption("📚 **Grounding Source Passages**:")
        for ref in source_references:
            st.caption(f"• *{ref}*")


def render_assessment_report_view(assessment_data: dict):
    """Render comprehensive radar chart and metrics report for evaluation."""
    st.markdown("### 📊 Comprehensive Mastery & Performance Report")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall Mastery Score", f"{int(assessment_data.get('mastery_score', 0.8) * 100)}%")
    col2.metric("Conceptual Clarity", f"{int(assessment_data.get('clarity_score', 0.85) * 100)}%")
    col3.metric("Application Skill", f"{int(assessment_data.get('application_score', 0.75) * 100)}%")
    col4.metric("Retention Index", f"{int(assessment_data.get('retention_score', 0.90) * 100)}%")

    st.divider()
    st.markdown("#### 🔍 Strengths & Actionable Recommendations")
    col_a, col_b = st.columns(2)
    with col_a:
        st.success("✅ **Demonstrated Strengths**")
        strengths = assessment_data.get("strengths", ["Understands core principles well", "Accurate formula application"])
        for s in strengths:
            st.markdown(f"- {s}")

    with col_b:
        st.warning("⚡ **Targeted Areas for Improvement**")
        improvements = assessment_data.get("improvements", ["Edge case boundary conditions", "Real-world scaling intuition"])
        for imp in improvements:
            st.markdown(f"- {imp}")


def render_system_status_card(state=None):
    """Render system status card on sidebar or footer."""
    if state and hasattr(state, 'profile') and state.profile:
        st.caption(f"🟢 **System Ready** | Learner: {state.profile.display_name} ({state.profile.language})")
    else:
        st.caption("🟢 **AI Teacher Engine Ready**")


render_report_view = render_assessment_report_view
