from dataclasses import dataclass


@dataclass
class Variable:
  """Variable keep values in config file."""

  def __init__(self) -> None:
    # display & input adjust
    self.zoom_ratio: float = 1.0
    self.random_offset: int = 0

    # timing & delays
    self.detect_delay: int = None
    self.restart_delay: int = None
    self.screenshot_delay: int = None
    self.freeze_threshold: int = None
    self.focus_threshold: int = None

    # file configuration
    self.config_file_name: str = "config.toml"  # constant
    self.update_file_name: str = "update.md"  # constant

    # bot modes
    self.emulator_mode: str = None
    self.control_mode: str = None
    self.adb_mode: str = None

    # ADB
    self.adb_port: str = None
    self.adb_ip: str = None
    self.adb_id: str = None

    # performance
    self.max_fps: int = None
    self.bitrate: int = None

    self.top_window: bool = None
    self.restart_app: bool = None
    self.notify_result: bool = None
    self.dev_mode: str = None
    self.line_notify_token: str = None

    # game statistic
    self.win: int = None
    self.lose: int = None

  def load_from_config_file(self) -> None:
    """Load config from file."""

  def save_to_config_file(self) -> None:
    """Save config to file."""
