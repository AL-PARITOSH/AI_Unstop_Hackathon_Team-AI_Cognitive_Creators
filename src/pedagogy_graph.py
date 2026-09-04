"""
LangGraph & Stateful Pedagogical Workflow Engine.
Implements finite deterministic state transitions and remediation limits.
"""

import logging
from typing import Dict, Any, Tuple
from src.schemas import (
    TeacherState, LessonPlan, LearnerProfileSchema, StudentEvaluation,
    AssessmentQuestion, AssessmentResultSchema, DoubtResponse, FlashcardDeck,
    LearningPathResponse
)
from src.prompts import (
    LESSON_PLANNER_SYSTEM_PROMPT, EVALUATOR_SYSTEM_PROMPT,
    ASSESSMENT_GENERATOR_PROMPT, FINAL_REPORT_PROMPT,
    DOUBT_SOLVER_PROMPT, FLASHCARD_GENERATOR_PROMPT,
    LEARNING_PATH_GENERATOR_PROMPT, CONCEPT_TRANSLATE_PROMPT
)
from src.llm_service import generate_structured_output
from src.rag_service import query_rag_context

logger = logging.getLogger(__name__)

class PedagogicalEngine:
    def __init__(self, state: TeacherState):
        self.state = state

    def plan_lesson(self) -> LessonPlan:
        """Node: UNDERSTAND_AND_PLAN - Generate curriculum lesson plan."""
        retrieved_context = ""
        if self.state.source_mode == "Document-grounded mode":
            search_query = self.state.topic
            if self.state.document_name and self.state.document_name not in search_query:
                search_query = f"{self.state.document_name} {search_query}"
            retrieved_context, chunks = query_rag_context(
                search_query, 
                top_k=6, 
                min_relevance_score=0.05, 
                document_name=self.state.document_name
            )
            if not chunks or retrieved_context == "insufficient_source_evidence":
                retrieved_context, _ = query_rag_context(
                    self.state.document_name or "textbook", 
                    top_k=6, 
                    min_relevance_score=0.01, 
                    document_name=self.state.document_name
                )

        time_mode = getattr(self.state.profile, 'time_mode', '20m')
        teacher_persona = getattr(self.state.profile, 'teacher_persona', 'dr_sarah')

        sys_prompt = LESSON_PLANNER_SYSTEM_PROMPT.format(
            topic=self.state.topic,
            source_mode=self.state.source_mode,
            language=self.state.profile.language,
            education_level=self.state.profile.education_level,
            prior_knowledge=self.state.profile.prior_knowledge,
            learning_goal=self.state.profile.learning_goal,
            preferred_style=self.state.profile.preferred_style,
            duration_minutes=self.state.profile.duration_minutes,
            time_mode=time_mode,
            teacher_persona=teacher_persona,
            desired_depth=self.state.profile.desired_depth,
            retrieved_context=retrieved_context
        )

        user_prompt = f"Create a personalized {time_mode} lesson plan for topic: '{self.state.topic}' in {self.state.profile.language} using teacher persona {teacher_persona}."
        
        lesson_plan = generate_structured_output(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            response_schema=LessonPlan
        )

        self.state.lesson_plan = lesson_plan
        self.state.current_concept_index = 0
        self.state.current_state = "EXPLAIN"
        return lesson_plan

    def evaluate_checkpoint_answer(self, student_answer: str) -> StudentEvaluation:
        """Node: EVALUATE - Grade answer, detect misconceptions, decide remediation."""
        if not self.state.lesson_plan or not self.state.lesson_plan.concepts:
            raise ValueError("No active lesson plan found to evaluate against.")

        concept = self.state.lesson_plan.concepts[self.state.current_concept_index]
        q_info = concept.checkpoint_question

        retrieved_context = ""
        if self.state.source_mode == "Document-grounded mode":
            retrieved_context, _ = query_rag_context(concept.title, top_k=3)

        sys_prompt = EVALUATOR_SYSTEM_PROMPT.format(
            concept_title=concept.title,
            language=self.state.profile.language,
            question_text=q_info.question_text,
            rubric=q_info.expected_answer_rubric,
            common_misconceptions=", ".join(q_info.common_misconceptions),
            student_answer=student_answer,
            retrieved_context=retrieved_context if retrieved_context != "insufficient_source_evidence" else ""
        )

        user_prompt = f"Evaluate this student answer: '{student_answer}' for concept '{concept.title}'."

        evaluation = generate_structured_output(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            response_schema=StudentEvaluation
        )

        # Track attempt and remediation count
        c_id = concept.concept_id
        current_remediation = self.state.concept_remediation_counts.get(c_id, 0)

        # Deterministic Routing Logic
        if evaluation.correctness_score >= 0.75:
            self.state.concept_mastery[c_id] = evaluation.correctness_score
            self.state.current_state = "ADVANCE"
        elif evaluation.correctness_score >= 0.40:
            self.state.concept_mastery[c_id] = evaluation.correctness_score
            self.state.current_state = "REINFORCE"
        else:
            # Score < 0.40: Remediation requested
            if current_remediation >= 2:
                # Max 2 remediations reached - force advance after warning
                logger.info(f"Max remediation count (2) reached for concept {c_id}. Forcing advance.")
                self.state.concept_mastery[c_id] = evaluation.correctness_score
                self.state.current_state = "ADVANCE"
                if evaluation.identified_misconception:
                    self.state.identified_misconceptions.append(evaluation.identified_misconception)
            else:
                self.state.concept_remediation_counts[c_id] = current_remediation + 1
                self.state.current_state = "REMEDIATE"
                if evaluation.identified_misconception:
                    self.state.identified_misconceptions.append(evaluation.identified_misconception)

        return evaluation

    def advance_concept(self) -> str:
        """Advance to next concept or trigger final assessment."""
        if not self.state.lesson_plan:
            return "FINAL_ASSESSMENT"

        num_concepts = len(self.state.lesson_plan.concepts)
        if self.state.current_concept_index + 1 < num_concepts:
            self.state.current_concept_index += 1
            self.state.current_state = "EXPLAIN"
        else:
            self.state.current_state = "FINAL_ASSESSMENT"
        return self.state.current_state

    def solve_student_doubt(self, student_question: str, language: str = None) -> DoubtResponse:
        """Answer an in-lesson student doubt in-character with proactive check-in."""
        if not self.state.lesson_plan or not self.state.lesson_plan.concepts:
            raise ValueError("No active lesson plan found.")

        concept = self.state.lesson_plan.concepts[self.state.current_concept_index]
        lang = language or self.state.profile.language
        persona = getattr(self.state.profile, 'teacher_persona', 'dr_sarah')

        sys_prompt = DOUBT_SOLVER_PROMPT.format(
            teacher_persona=persona,
            lesson_title=self.state.lesson_plan.lesson_title,
            concept_title=concept.title,
            spoken_script=concept.spoken_script,
            analogy=concept.simple_analogy,
            student_question=student_question,
            language=lang
        )
        user_prompt = f"Student asks: '{student_question}'. Explain clearly as {persona} in {lang}."

        try:
            return generate_structured_output(
                system_prompt=sys_prompt,
                user_prompt=user_prompt,
                response_schema=DoubtResponse
            )
        except Exception as e:
            logger.warning(f"Fallback doubt solver triggered: {e}")
            if lang == "Hindi":
                ans = f"Bahut accha sawal! {concept.title} ke bare me samajhna aasan hai: {concept.simple_analogy}. Yeh siddhant system ke sabhi hisson ko jode rakhta hai."
                takeaway = f"{concept.title} ka mukhya niyam samajhna aavashyak hai."
                followup = "Kya aapko yeh samajh aaya, ya koi aur udaaharan chahiye?"
            else:
                ans = f"That's a very insightful question! Regarding {concept.title}: remember the mental model that {concept.simple_analogy}. This explains why the values respond dynamically to changes."
                takeaway = f"Core takeaway: {concept.title} governs how each element reacts under operating conditions."
                followup = "Does this mental model make sense, or would you like a practical calculation example?"
            return DoubtResponse(
                answer_text=ans,
                key_takeaway=takeaway,
                follow_up_prompt=followup
            )

    def generate_flashcards(self) -> FlashcardDeck:
        """Generate high-yield active recall flashcard deck from current lesson plan."""
        if not self.state.lesson_plan:
            raise ValueError("No active lesson plan to generate flashcards from.")

        summary_lines = []
        for i, c in enumerate(self.state.lesson_plan.concepts):
            summary_lines.append(f"Concept {i+1}: {c.title}. Analogy: {c.simple_analogy}. Key takeaways: {', '.join(c.key_points)}")

        sys_prompt = FLASHCARD_GENERATOR_PROMPT.format(
            lesson_title=self.state.lesson_plan.lesson_title,
            concepts_summary="\n".join(summary_lines),
            language=self.state.profile.language
        )
        user_prompt = f"Generate active recall flashcards for lesson: '{self.state.lesson_plan.lesson_title}' in {self.state.profile.language}."

        try:
            return generate_structured_output(
                system_prompt=sys_prompt,
                user_prompt=user_prompt,
                response_schema=FlashcardDeck
            )
        except Exception as e:
            logger.warning(f"Fallback flashcards triggered: {e}")
            from src.schemas import Flashcard
            cards = []
            for i, c in enumerate(self.state.lesson_plan.concepts):
                first_pt = c.key_points[0] if c.key_points else c.title
                cards.append(Flashcard(
                    id=f"fc_{i+1}",
                    front_question=f"What is the fundamental mechanism behind {c.title}?",
                    back_explanation=f"{c.title} operates on the principle that: {c.simple_analogy}. Key rule: {first_pt}.",
                    difficulty=c.difficulty,
                    analogy_or_mnemonic=c.simple_analogy
                ))
            return FlashcardDeck(
                lesson_title=self.state.lesson_plan.lesson_title,
                flashcards=cards
            )

    @classmethod
    def generate_learning_path(cls, topic: str, education_level: str = "beginner", language: str = "Hinglish") -> LearningPathResponse:
        """Generate an 6-8 stage progressive learning path for a broad topic."""
        sys_prompt = LEARNING_PATH_GENERATOR_PROMPT.format(
            topic=topic,
            education_level=education_level,
            language=language
        )
        user_prompt = f"Design a comprehensive structured learning path for topic '{topic}' suitable for {education_level} level in {language}."

        try:
            return generate_structured_output(
                system_prompt=sys_prompt,
                user_prompt=user_prompt,
                response_schema=LearningPathResponse
            )
        except Exception as e:
            logger.warning(f"Fallback learning path generator triggered: {e}")
            from src.schemas import LearningPathStage
            stages = [
                LearningPathStage(
                    stage_number=1,
                    title=f"Core Intuition & Terminology of {topic}",
                    description=f"Establish mental models, foundational definitions, and introductory principles of {topic}.",
                    key_skills=["Foundational Terminology", "Intuitive Models", "Core Mechanics"],
                    estimated_hours=4,
                    is_unlocked=True,
                    is_completed=False,
                    difficulty="beginner"
                ),
                LearningPathStage(
                    stage_number=2,
                    title=f"Theoretical Frameworks & Mathematical Foundations",
                    description=f"Deep dive into governing equations, analytical models, and theoretical formulations for {topic}.",
                    key_skills=["Mathematical Formulation", "Derivations", "Analytical Reasoning"],
                    estimated_hours=6,
                    is_unlocked=False,
                    is_completed=False,
                    difficulty="intermediate"
                ),
                LearningPathStage(
                    stage_number=3,
                    title=f"Hands-On Applications & Problem Solving Patterns",
                    description=f"Practical workflows, calculation patterns, and architectural implementations for {topic}.",
                    key_skills=["Hands-on Applications", "Problem Solving Patterns", "Implementation"],
                    estimated_hours=8,
                    is_unlocked=False,
                    is_completed=False,
                    difficulty="intermediate"
                ),
                LearningPathStage(
                    stage_number=4,
                    title=f"Advanced Architectures, Edge Cases & Optimization",
                    description=f"Scaling up, efficiency bottlenecks, edge-case remediation, and production-grade optimization in {topic}.",
                    key_skills=["Optimization", "Scalability", "System Architecture"],
                    estimated_hours=10,
                    is_unlocked=False,
                    is_completed=False,
                    difficulty="advanced"
                ),
                LearningPathStage(
                    stage_number=5,
                    title=f"Comprehensive Capstone Project & Mastery Evaluation",
                    description=f"Integrated capstone project synthesizing all preceding concepts into a production-level deliverable.",
                    key_skills=["End-to-End Capstone", "System Integration", "Rigorous Evaluation"],
                    estimated_hours=12,
                    is_unlocked=False,
                    is_completed=False,
                    difficulty="advanced"
                )
            ]
            return LearningPathResponse(
                topic=topic,
                target_audience=education_level,
                total_stages=len(stages),
                total_hours=sum(s.estimated_hours for s in stages),
                stages=stages
            )

    def translate_concept(self, concept_idx: int, target_language: str) -> Dict[str, Any]:
        """Translate and re-narrate a specific concept in a new language."""
        if not self.state.lesson_plan or concept_idx >= len(self.state.lesson_plan.concepts):
            raise ValueError("Invalid concept index.")

        concept = self.state.lesson_plan.concepts[concept_idx]
        sys_prompt = CONCEPT_TRANSLATE_PROMPT.format(
            target_language=target_language,
            title=concept.title,
            spoken_script=concept.spoken_script,
            simple_analogy=concept.simple_analogy,
            whiteboard_points=", ".join(concept.whiteboard_bullet_points)
        )
        user_prompt = f"Re-narrate concept '{concept.title}' into {target_language}."

        import json
        from src.llm_service import generate_raw_chat_completion
        raw_res = generate_raw_chat_completion(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        try:
            return json.loads(raw_res)
        except Exception:
            return {
                "concept_title": concept.title,
                "spoken_script": concept.spoken_script,
                "simple_analogy": concept.simple_analogy,
                "whiteboard_bullet_points": concept.whiteboard_bullet_points
            }

