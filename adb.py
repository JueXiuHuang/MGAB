from typing import Any, Callable

import scrcpy
from adbutils import adb, AdbDevice

from mode import ADBMode


class ADB:
  def __init__(self, package_name: str) -> None:
    self.package_name = package_name
    self.d: AdbDevice = None
    self.client: scrcpy.Client = None
    self.adb_device_code: str = ""
    self.frame = None

  def click(self, xy: tuple[int, int]) -> None:
    self.d.click(xy[0], xy[1])

  def swipe(self, src: tuple[int, int], dst: tuple[int, int], time: float) -> None:
    self.d.swipe(src[0], src[1], dst[0], dst[1], time)

  def touch(self, xy: tuple[int, int], action: int) -> bytes:
    return self.client.control.touch(xy[0], xy[1], action)

  def back(self) -> None:
    self.d.keyevent("KEYCODE_BACK")

  def home(self) -> None:
    self.d.keyevent("HOME")

  def getResolution(self) -> tuple[int, int] | None:
    return self.client.resolution

  def screenshot(self) -> Any:
    while self.frame is None:
      pass
    return self.frame

  def connect(self, mode: ADBMode, ip: str, port: int, id: str) -> tuple[str, bool]:
    if mode == ADBMode.IP:
      self.adb_device_code = f"{ip}:{port}"
      output = adb.connect(self.adb_device_code)
      success = "connected" in output
      r = (output, success)
      if success:
        self.d = adb.device(serial=self.adb_device_code)
    elif mode == ADBMode.ID:
      self.adb_device_code = id
      self.d = adb.device(serial=id)
      r = ("Use device ID, skip connection", True)

    return r

  def createClient(
    self, mode: ADBMode, max_fps: int, bitrate: int, updateScreen: Callable
  ) -> None:
    # add screenshot listener
    def on_frame(frame):
      # If you set non-blocking (default) in constructor, the frame event receiver
      # may receive None to avoid blocking event.
      if frame is not None:
        self.frame = frame
        updateScreen(frame)

    self.client = scrcpy.Client(
      device=self.d, max_fps=max_fps, bitrate=bitrate, flip=(mode == ADBMode.IP)
    )
    self.client.add_listener(scrcpy.EVENT_FRAME, on_frame)
    self.client.start(threaded=True)

  def disconnect(self) -> None:
    if self.client is not None:
      self.client.stop()
    if self.adb_device_code != "":
      adb.disconnect(self.adb_device_code)

  def detectApp(self) -> tuple[bool, str]:
    app_info = self.d.app_current()
    return (self.package_name in app_info.package, app_info.package)

  def restart(self) -> None:
    self.d.app_stop(self.package_name)
    self.d.app_start(self.package_name)
