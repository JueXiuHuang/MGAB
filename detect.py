import joblib

from models.interface import MLProtocol, MockOCR


def load_model(path: str) -> MLProtocol:
  return joblib.load(path)


class Detect:
  def __init__(self) -> None:
    self.ocr_model = MockOCR
    pass
