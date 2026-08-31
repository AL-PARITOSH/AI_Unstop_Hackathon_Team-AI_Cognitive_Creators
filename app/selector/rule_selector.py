from typing import List
from app.models.request import VisualRequest
from app.selector.base import BaseVisualSelector, SelectorResult
from app.selector.rules import RuleEngine
from app.selector.taxonomy import SUPPORTED_VISUAL_TYPES, SECONDARY_VISUAL_MAP
from app.config import settings

class RuleBasedVisualSelector(BaseVisualSelector):
    """
    100% deterministic, offline visual type selector with domain heuristics,
    confidence calibration, multi-visual recommendation, and safe fallback.
    """

    def select(self, request: VisualRequest) -> SelectorResult:
        # 1. Check explicit user override
        if request.visual_type_override:
            override = request.visual_type_override.lower().strip()
            if override in SUPPORTED_VISUAL_TYPES:
                secondary = [t for t in SUPPORTED_VISUAL_TYPES if t != override][:2]
                return SelectorResult(
                    primary_type=override,
                    secondary_types=secondary if request.include_secondary else [],
                    confidence=1.0,
                    reason=f"User explicitly requested visual type '{override}'.",
                    suggested_visual_types=[override] + secondary
                )

        # 2. Check exact curriculum concept match
        exact_match = RuleEngine.match_exact_concept(request.concept)
        if exact_match:
            primary, secondary, conf, reason = exact_match
            suggested = [primary] + [s for s in secondary if s != primary]
            for vt in SUPPORTED_VISUAL_TYPES:
                if vt not in suggested:
                    suggested.append(vt)

            return SelectorResult(
                primary_type=primary,
                secondary_types=secondary if request.include_secondary else [],
                confidence=conf,
                reason=reason,
                suggested_visual_types=suggested
            )

        # 3. Score all visual types based on taxonomy & context
        scores = RuleEngine.score_visual_types(
            topic=request.topic,
            concept=request.concept,
            context=request.lesson_context or ""
        )

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best_type, best_score = ranked[0]

        # Normalize confidence to [0.2, 0.95]
        normalized_confidence = min(0.95, max(0.2, best_score))

        # Check secondary types
        c_norm = RuleEngine.normalize(request.concept)
        secondary_list: List[str] = []
        for key, secs in SECONDARY_VISUAL_MAP.items():
            if key in c_norm:
                secondary_list = [s for s in secs if s != best_type]
                break

        if not secondary_list and len(ranked) > 1 and ranked[1][1] > 0.2:
            secondary_list = [ranked[1][0]]

        suggested_types = [t for t, _ in ranked]

        # 4. Safe fallback if confidence is low
        if normalized_confidence < settings.CONFIDENCE_THRESHOLD_SAFE_FALLBACK:
            fallback_type = "diagram"  # Safe generic structured concept diagram
            return SelectorResult(
                primary_type=fallback_type,
                secondary_types=["flowchart"] if request.include_secondary else [],
                confidence=normalized_confidence,
                reason=f"Concept '{request.concept}' has ambiguous visual cues (confidence: {normalized_confidence:.2f}). Defaulting to safe conceptual diagram fallback.",
                suggested_visual_types=[fallback_type, "flowchart", "formula", "graph", "timeline", "code_execution", "architecture"]
            )

        reason = f"Concept '{request.concept}' in domain '{request.topic}' strongly aligns with visual representation '{best_type}'."

        return SelectorResult(
            primary_type=best_type,
            secondary_types=secondary_list if request.include_secondary else [],
            confidence=round(normalized_confidence, 2),
            reason=reason,
            suggested_visual_types=suggested_types
        )
