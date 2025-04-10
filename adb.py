from collections.abc import Callable
from typing import Any, TypeVar

import scrcpy
from adbutils import AdbDevice, adb

from mode import ADBMode

T = TypeVar("T")


def singleton(cls: type[T]) -> Callable[..., T]:
  instances = {}

  def get_instance(*args: tuple, **kwargs: dict[str, Any]) -> T:
    if cls not in instances:
      instances[cls] = cls(*args, **kwargs)
    return instances[cls]

  return get_instance


@singleton
class ADB:
  def __init__(self, package_name: str) -> None:
    """Initialize a adb object with given package name."""
    self.package_name = package_name
    self.d: AdbDevice = None
    self.client: scrcpy.Client = None
    self.adb_device_code: str = ""
    self.frame = None

  def click(self, xy: tuple[int, int]) -> None:
    """Simulate android click on given position."""
    self.d.click(xy[0], xy[1])

  def swipe(self, src: tuple[int, int], dst: tuple[int, int], time: float) -> None:
    """Swipe from start point to end point."""
    self.d.swipe(src[0], src[1], dst[0], dst[1], time)

  def touch(self, xy: tuple[int, int], action: int) -> bytes:
    """Touch screen."""
    return self.client.control.touch(xy[0], xy[1], action)

  def back(self) -> None:
    """Simulate android BACK event."""
    self.d.keyevent("KEYCODE_BACK")

  def home(self) -> None:
    """Simulate android HOME event."""
    self.d.keyevent("HOME")

  def get_resolution(self) -> tuple[int, int] | None:
    """Get android device's resolution if client exist."""
    return self.client.resolution

  def screenshot(self) -> Any:
    """Wait until client get a screenshot."""
    while self.frame is None:
      pass
    return self.frame

  def connect(self, mode: ADBMode, ip: str, port: int, device_id: str) -> tuple[str, bool]:
    """Connect to a android device."""
    if mode == ADBMode.IP:
      self.adb_device_code = f"{ip}:{port}"
      output = adb.connect(self.adb_device_code)
      success = "connected" in output
      r = (output, success)
      if success:
        self.d = adb.device(serial=self.adb_device_code)
    elif mode == ADBMode.ID:
      self.adb_device_code = id
      self.d = adb.device(serial=device_id)
      r = ("Use device ID, skip connection", True)

    return r

  def create_client(self, mode: ADBMode, max_fps: int, bitrate: int, update_screen: Callable) -> None:
    # add screenshot listener
    def on_frame(frame):
      # If you set non-blocking (default) in constructor, the frame event receiver
      # may receive None to avoid blocking event.
      if frame is not None:
        self.frame = frame
        update_screen(frame)

    self.client = scrcpy.Client(device=self.d, max_fps=max_fps, bitrate=bitrate, flip=(mode == ADBMode.IP))
    self.client.add_listener(scrcpy.EVENT_FRAME, on_frame)
    self.client.start(threaded=True)

  def disconnect(self) -> None:
    """Disconnect from a client."""
    if self.client is not None:
      self.client.stop()
    if self.adb_device_code != "":
      adb.disconnect(self.adb_device_code)

  def detect_app(self) -> tuple[bool, str]:
    """Detect if the device is running the app."""
    app_info = self.d.app_current()
    return (self.package_name in app_info.package, app_info.package)

  def restart(self) -> None:
    """Restart the app."""
    self.d.app_stop(self.package_name)
    self.d.app_start(self.package_name)
