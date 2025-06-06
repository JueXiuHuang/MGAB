import logging
from pathlib import Path

import toml
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class DisplayInputAdjust(BaseModel):
  zoom_ratio: float = 1.0
  random_offset: int = Field(default=0, ge=0)


class TimingDelays(BaseModel):
  detect_delay: int = Field(default=0, ge=0)
  restart_delay: int = Field(default=0, ge=0)
  screenshot_delay: int = Field(default=0, ge=0)
  freeze_threshold: int = Field(default=0, ge=0)
  focus_threshold: int = Field(default=0, ge=0)


class BotModes(BaseModel):
  emulator_mode: str = None
  control_mode: str = None
  adb_mode: str = None


class AdbSettings(BaseModel):
  adb_port: str = Field(default="5555")
  adb_ip: str = Field(default="127.0.0.1")
  adb_id: str = None


class PerformanceSettings(BaseModel):
  max_fps: int = Field(default=120, gt=0)
  bitrate: int = Field(default=12000, gt=0)


class GeneralFlags(BaseModel):
  top_window: bool = False
  restart_app: bool = False
  notify_result: bool = False
  dev_mode: bool = False
  line_notify_token: str = None
  package: str = None


class AppConfig(BaseModel):
  display_input: DisplayInputAdjust = Field(default_factory=DisplayInputAdjust)
  timing: TimingDelays = Field(default_factory=TimingDelays)
  modes: BotModes = Field(default_factory=BotModes)
  adb: AdbSettings = Field(default_factory=AdbSettings)
  performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
  general: GeneralFlags = Field(default_factory=GeneralFlags)

  @classmethod
  def load_from_file(cls, file_path: str | Path = "config.toml") -> "AppConfig":
    """Load from toml and verify data."""
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
      logger.warning("Warning: Configuration file '%s' not found. Returning default configuration.", file_path_obj)
      return cls()

    try:
      with file_path_obj.open("r", encoding="utf-8") as f:
        data_from_toml = toml.load(f)
      return cls(**data_from_toml)
    except toml.TomlDecodeError as e:
      logger.warning("Error decoding TOML file '%s': %s", file_path_obj, e)
      logger.warning("Returning default configuration.")
      return cls()
    except ValidationError as e:
      logger.warning("Configuration validation error from file '%s': %s", file_path_obj, e)
      logger.warning("Please check your config.toml structure. Returning default configuration.")
      return cls()
    except Exception as e:
      logger.exception("An unexpected error occurred while loading config '%s': %s", file_path_obj, e)
      logger.warning("Returning default configuration.")
      return cls()

  def save_to_file(self, file_path: str | Path = "config.toml") -> None:
    """Save to toml."""
    file_path_obj = Path(file_path)
    try:
      config_dict = self.model_dump(mode="python")
      with file_path_obj.open("w", encoding="utf-8") as f:
        toml.dump(config_dict, f)
      logger.info("Configuration successfully saved to '%s'.", file_path_obj)
    except Exception as e:
      logger.exception("Error saving configuration to '%s': %s", file_path_obj, e)
