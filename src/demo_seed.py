"""
Demo Seed Scenario for Ohm's Law Hackathon Walkthrough.
"""

from src.schemas import (
    TeacherState, LessonPlan, ConceptPlan, VisualSpec,
    CheckpointQuestion, LearnerProfileSchema, StudentEvaluation
)

def get_ohms_law_demo_state() -> TeacherState:
    """Pre-configured Ohm's Law interactive demo state."""
    profile = LearnerProfileSchema(
        display_name="Demo Student",
        education_level="beginner",
        prior_knowledge="basic",
        learning_goal="Master Ohm's Law and basic electric circuits",
        preferred_style="visual-first",
        language="Hinglish",
        voice_preference="female",
        duration_minutes=20,
        desired_depth="standard lesson"
    )

    c1 = ConceptPlan(
        concept_id="concept_1",
        title="Voltage, Current, and Resistance Fundamentals",
        prerequisite_ids=[],
        estimated_minutes=6,
        difficulty="easy",
        spoken_script="Namaste! Aaj hum Ohm's Law ke core pillars - Voltage, Current, aur Resistance ko samjhenge. Think of Voltage as electrical pressure, Current as charge flow, and Resistance as opposition to that flow.",
        whiteboard_bullet_points=[
            "Voltage (V): Electrical potential difference measured in Volts",
            "Current (I): Rate of charge flow measured in Amperes",
            "Resistance (R): Opposition to electric flow measured in Ohms (Ω)"
        ],
        simple_analogy="Isse ek water pipe ki tarah socho: Voltage water pressure hai, Current water flow volume hai, aur Resistance pipe me laga narrowing valve hai.",
        worked_example="If Voltage V = 12V and Resistance R = 4 Ω, Current I = V / R = 12 / 4 = 3 Amperes.",
        visual=VisualSpec(
            visual_type="graph",
            title="Ohm's Law: Voltage vs Current Plot",
            specification="V = I * R coordinate graph showing linear current response for R = 2 Ω and R = 4 Ω",
            caption="Notice how higher resistance produces a shallower line (lower current for same voltage)."
        ),
        key_points=[
            "Current increases when Voltage increases.",
            "Current decreases when Resistance increases."
        ],
        checkpoint_question=CheckpointQuestion(
            question_id="chk_1",
            question_type="conceptual",
            question_text="If voltage V remains constant and resistance R increases, what happens to current I?",
            expected_answer_rubric="Current I decreases because current is inversely proportional to resistance (I = V / R).",
            common_misconceptions=["Thinking current increases with resistance", "Thinking current stays unchanged"]
        ),
        remediation_strategies=[
            "Water pipe narrowing analogy",
            "Inverse mathematical relationship visualization (I = V/R)"
        ]
    )

    c2 = ConceptPlan(
        concept_id="concept_2",
        title="Mathematical Formula V = I × R and Circuit Calculations",
        prerequisite_ids=["concept_1"],
        estimated_minutes=7,
        difficulty="medium",
        spoken_script="Ab hum Ohm's Law ka mathematical formula V = I × R apply karenge. Is formula triangle ko yaad rakho: V top par, I aur R bottom par.",
        whiteboard_bullet_points=[
            "Formula: V = I × R",
            "Current: I = V / R",
            "Resistance: R = V / I"
        ],
        simple_analogy="Ohm's Law Triangle makes rearranging equations effortless.",
        worked_example="Battery Voltage V = 24V, Bulb Resistance R = 6 Ω. Current I = 24 / 6 = 4 Amperes.",
        visual=VisualSpec(
            visual_type="formula",
            title="Ohm's Law Formula Triangle",
            specification="V = I \\times R \\quad \\implies \\quad I = \\frac{V}{R}",
            caption="Ohm's Law algebraic relationships."
        ),
        key_points=[
            "V, I, and R are strictly linked by V = I × R."
        ],
        checkpoint_question=CheckpointQuestion(
            question_id="chk_2",
            question_type="short_answer",
            question_text="Calculate current I if voltage V = 30 Volts and resistance R = 10 Ohms.",
            expected_answer_rubric="I = 30 / 10 = 3 Amperes.",
            common_misconceptions=["Multiplying instead of dividing 30 * 10 = 300"]
        )
    )

    plan = LessonPlan(
        lesson_title="Ohm's Law & Circuit Analysis Masterclass",
        learner_profile_summary="Beginner | Hinglish | Visual-First | 20 Mins",
        source_mode="General knowledge topic mode",
        language="Hinglish",
        total_duration_minutes=20,
        learning_objectives=[
            "Understand electrical Voltage, Current, and Resistance intuitively",
            "Apply Ohm's Law V = I × R to solve circuit problems",
            "Analyze inverse proportionality between Resistance and Current"
        ],
        concepts=[c1, c2]
    )

    state = TeacherState(
        topic="Ohm's Law",
        source_mode="General knowledge topic mode",
        profile=profile,
        lesson_plan=plan,
        current_concept_index=0,
        current_state="CHECKPOINT"
    )
    return state


def get_demo_misconception_remediation() -> StudentEvaluation:
    """Pre-packaged remediation evaluation for student's incorrect answer: 'Current increases'."""
    return StudentEvaluation(
        correctness_score=0.10,
        confidence=0.95,
        concept_mastery="low",
        identified_misconception="Confusing inverse proportionality (Thinking higher resistance causes higher current)",
        supporting_evidence="Student stated 'Current increases' when resistance increased under constant voltage.",
        feedback_to_student="Aapne socha ki resistance badhne se current badhega, lekin asal me resistance current ko ROKTA (oppose करता) hai!",
        recommended_action="remediate",
        remediation_script="Dhyan se samjho: Resistance electric current ke raaste me ek FRICTION ya OBSTACLE ki tarah hai. Agar hum rasta zyada narrow kar denge (higher R), to paani ka flow (Current I) KAM ho jayega. Formula I = V / R me dekho: R denominator me hai, so Jab R badhega, Current I DECREASE hoga!",
        remediation_visual=VisualSpec(
            visual_type="formula",
            title="Inverse Proportionality Remediation",
            specification="I = \\frac{V}{R} \\quad (R \\uparrow \\implies I \\downarrow)",
            caption="When Resistance R increases under constant Voltage V, Current I MUST decrease."
        ),
        re_check_question=CheckpointQuestion(
            question_id="chk_1_recheck",
            question_type="conceptual",
            question_text="If a lightbulb's wire gets thinner (higher resistance) while connected to the same 12V battery, will the current through it INCREASE or DECREASE?",
            expected_answer_rubric="Current will DECREASE due to higher resistance.",
            common_misconceptions=["Saying current increases"]
        )
    )
