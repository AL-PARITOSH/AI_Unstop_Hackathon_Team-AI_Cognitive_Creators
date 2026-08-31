from abc import ABC, abstractmethod
from app.models.request import VisualRequest
from app.models.specs.base import BaseVisualSpec

class BaseSpecGenerator(ABC):
    @abstractmethod
    def generate(self, request: VisualRequest, visual_type: str) -> BaseVisualSpec:
        """Generates a strongly typed visual specification from the request."""
        pass
