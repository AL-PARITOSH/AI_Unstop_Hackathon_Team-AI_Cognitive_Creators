from app.models.request import VisualRequest
from app.models.specs.base import BaseVisualSpec
from app.generators.knowledge_base import CurriculumKnowledgeBase
from app.generators.dynamic_builder import DynamicSpecBuilder
from app.selector.rules import RuleEngine

class SpecGeneratorRegistry:
    """
    Central registry routing requests to curriculum knowledge base templates
    or dynamic specification generators.
    """

    @staticmethod
    def generate(request: VisualRequest, visual_type: str) -> BaseVisualSpec:
        c = RuleEngine.normalize(request.concept)

        # 1. Newton's Second Law
        if "newton" in c:
            return CurriculumKnowledgeBase.get_newtons_second_law(visual_type)

        # 2. Ohm's Law
        if "ohm" in c:
            return CurriculumKnowledgeBase.get_ohms_law(visual_type)

        # 3. Photosynthesis
        if "photosynthesis" in c:
            return CurriculumKnowledgeBase.get_photosynthesis(visual_type)

        # 4. Binary Search
        if "binary search" in c:
            return CurriculumKnowledgeBase.get_binary_search(visual_type)

        # 5. Python for loop
        if "for loop" in c or "python loop" in c or ("python" in c and "loop" in c):
            return CurriculumKnowledgeBase.get_python_for_loop(visual_type)

        # 6. Machine Learning pipeline
        if "machine learning" in c or "ml pipeline" in c or ("pipeline" in c and "learning" in c):
            return CurriculumKnowledgeBase.get_ml_pipeline(visual_type)

        # 7. French Revolution
        if "french revolution" in c or ("revolution" in c and "timeline" in c):
            return CurriculumKnowledgeBase.get_french_revolution(visual_type)

        # 8. y = x^2
        if "y = x" in c or "x^2" in c or "x²" in c or "parabola" in c:
            return CurriculumKnowledgeBase.get_y_equals_x_squared(visual_type)

        # Dynamic fallback
        return DynamicSpecBuilder.build(request, visual_type)
