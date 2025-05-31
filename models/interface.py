from typing import Any, Protocol

from PIL import Image


class MLProtocol(Protocol):
  """A protocol for machine learning models."""

  def predict(self, image: Image.Image) -> Any: ...


class MockOCR:
  def predict(self, _: Image.Image) -> Any:
    """Mock prediction method that returns a fixed string."""
    return "single OCR result"
