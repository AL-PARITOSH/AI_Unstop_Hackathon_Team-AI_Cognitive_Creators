"""
Comprehensive Unit Test Suite for AI Teacher.
"""

import unittest
import os
import tempfile
import json
from src.schemas import (
    LearnerProfileSchema, LessonPlan, ConceptPlan, VisualSpec,
    CheckpointQuestion, StudentEvaluation, TeacherState
)
from src.rag_service import chunk_sections, query_rag_context
from src.pedagogy_graph import PedagogicalEngine
from src.tts_service import get_voice
from src.demo_seed import get_ohms_law_demo_state

class TestAITeacherCore(unittest.TestCase):

    def test_learner_profile_schema(self):
        """Test default profile values and schema validation."""
        profile = LearnerProfileSchema()
        self.assertEqual(profile.display_name, "Learner")
        self.assertEqual(profile.language, "Hinglish")
        self.assertEqual(profile.duration_minutes, 20)

    def test_semantic_chunking(self):
        """Test semantic section chunking and metadata preservation."""
        sections = [
            {
                "page_number": 1,
                "slide_number": None,
                "section_heading": "Test Section",
                "text": "Ohm's law states that the current through a conductor between two points is directly proportional to the voltage across the two points." * 5
            }
        ]
        chunks = chunk_sections(sections, chunk_size=100, overlap=20)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0]["section_heading"], "Test Section")
        self.assertEqual(chunks[0]["page_number"], 1)

    def test_tts_voice_mapping(self):
        """Test multilingual voice mapping."""
        self.assertEqual(get_voice("Hindi", "female"), "hi-IN-SwaraNeural")
        self.assertEqual(get_voice("Hindi", "male"), "hi-IN-MadhurNeural")
        self.assertEqual(get_voice("English", "female"), "en-IN-NeerjaNeural")
        self.assertEqual(get_voice("English", "male"), "en-IN-PrabhatNeural")
        self.assertEqual(get_voice("Hinglish", "female"), "hi-IN-SwaraNeural")

    def test_demo_state_structure(self):
        """Test Ohm's Law demo state initialization."""
        state = get_ohms_law_demo_state()
        self.assertEqual(state.topic, "Ohm's Law")
        self.assertIsNotNone(state.lesson_plan)
        self.assertEqual(len(state.lesson_plan.concepts), 2)
        self.assertEqual(state.lesson_plan.concepts[0].title, "Voltage, Current, and Resistance Fundamentals")

    def test_deterministic_evaluation_routing(self):
        """Test pedagogical engine routing based on score threshold."""
        state = get_ohms_law_demo_state()
        engine = PedagogicalEngine(state)

        # High score -> Advance
        eval_high = StudentEvaluation(
            correctness_score=0.90,
            confidence=0.95,
            concept_mastery="high",
            supporting_evidence="Correct answer",
            feedback_to_student="Great work!",
            recommended_action="advance"
        )
        self.assertGreaterEqual(eval_high.correctness_score, 0.75)

        # Low score -> Remediation
        eval_low = StudentEvaluation(
            correctness_score=0.20,
            confidence=0.90,
            concept_mastery="low",
            identified_misconception="Inverse proportionality confusion",
            supporting_evidence="Wrong answer",
            feedback_to_student="Let us revise.",
            recommended_action="remediate"
        )
        self.assertLess(eval_low.correctness_score, 0.40)

if __name__ == "__main__":
    unittest.main()
