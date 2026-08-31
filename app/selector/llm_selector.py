from app.models.request import VisualRequest
from app.selector.base import BaseVisualSelector, SelectorResult
from app.selector.rule_selector import RuleBasedVisualSelector

class LLMVisualSelector(BaseVisualSelector):
    """
    Extension point for optional LLM-assisted visual selection.
    Delegates to RuleBasedVisualSelector by default so no API key or external LLM is required.
    Another team can subclass or configure this with OpenAI/Gemini/Ollama later.
    """
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.fallback_selector = RuleBasedVisualSelector()

    def select(self, request: VisualRequest) -> SelectorResult:
        # In offline/standalone mode, we use the deterministic rule-based selector
        if not self.api_key:
            res = self.fallback_selector.select(request)
            return SelectorResult(
                primary_type=res.primary_type,
                secondary_types=res.secondary_types,
                confidence=res.confidence,
                reason=res.reason + " (Offline Rule-Based Selector)",
                suggested_visual_types=res.suggested_visual_types
            )
        
        # When an LLM client is configured, external team can inject custom reasoning here
        return self.fallback_selector.select(request)
