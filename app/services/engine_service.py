from typing import Optional, List, Dict, Any
from app.models.request import VisualRequest
from app.models.response import VisualResponse, VisualItem, SelectorMetadata
from app.selector.base import BaseVisualSelector
from app.selector.rule_selector import RuleBasedVisualSelector
from app.generators.registry import SpecGeneratorRegistry
from app.renderers.registry import RendererRegistry
from app.services.storage_service import StorageService

class VisualEngineService:
    """
    Main orchestration service coordinating Visual Selector, Spec Generators,
    Renderers, and Artifact Storage.
    """

    def __init__(self, selector: Optional[BaseVisualSelector] = None):
        self.selector = selector or RuleBasedVisualSelector()

    def generate_visual(self, request: VisualRequest) -> VisualResponse:
        # 1. Select visual type(s)
        sel_result = self.selector.select(request)
        primary_type = sel_result.primary_type

        # 2. Generate Primary Visual Spec
        primary_spec = SpecGeneratorRegistry.generate(request, primary_type)

        # 3. Render Primary Visual
        primary_rendered = RendererRegistry.render(primary_spec)

        # 4. Save Primary Artifact and get URL
        primary_id = StorageService.generate_visual_id(request.concept, primary_type)
        StorageService.save_visual_artifact(primary_id, primary_rendered.full_html_page)
        primary_url = StorageService.get_visual_url(primary_id)

        # 5. Format primary visual_data
        primary_data: Dict[str, Any] = {
            "format": primary_rendered.format,
            "raw_svg": primary_rendered.raw_svg,
            "rendered_html": primary_rendered.raw_html,
            "plotly_json": primary_rendered.plotly_dict,
            "latex": primary_rendered.latex_str,
            "spec": primary_spec.model_dump()
        }

        # 6. Generate Secondary Visuals if requested
        secondary_items: List[VisualItem] = []
        if request.include_secondary and sel_result.secondary_types:
            for sec_type in sel_result.secondary_types:
                if sec_type == primary_type:
                    continue

                sec_spec = SpecGeneratorRegistry.generate(request, sec_type)
                sec_rendered = RendererRegistry.render(sec_spec)
                sec_id = StorageService.generate_visual_id(request.concept, sec_type)
                StorageService.save_visual_artifact(sec_id, sec_rendered.full_html_page)
                sec_url = StorageService.get_visual_url(sec_id)

                sec_data: Dict[str, Any] = {
                    "format": sec_rendered.format,
                    "raw_svg": sec_rendered.raw_svg,
                    "rendered_html": sec_rendered.raw_html,
                    "plotly_json": sec_rendered.plotly_dict,
                    "latex": sec_rendered.latex_str,
                    "spec": sec_spec.model_dump()
                }

                secondary_items.append(
                    VisualItem(
                        visual_type=sec_type,
                        title=sec_spec.title,
                        explanation=sec_spec.explanation,
                        visual_data=sec_data,
                        visual_url=sec_url
                    )
                )

        # 7. Construct and return final VisualResponse
        metadata = SelectorMetadata(
            confidence=sel_result.confidence,
            reason=sel_result.reason,
            suggested_visual_types=sel_result.suggested_visual_types
        )

        return VisualResponse(
            visual_type=primary_type,
            title=primary_spec.title,
            explanation=primary_spec.explanation,
            selector_metadata=metadata,
            visual_data=primary_data,
            visual_url=primary_url,
            secondary_visuals=secondary_items
        )
