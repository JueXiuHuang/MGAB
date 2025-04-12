import math
import time
from abc import ABC, abstractmethod

import win32api
import win32con

from adb import ADB


class ControlInterface(ABC):
  """Define basic control interface for a game."""

  @abstractmethod
  def adb(self) -> ADB:
    """Dynamically get ADB instance."""

  @abstractmethod
  def tap(self, pos: tuple[int, int]) -> None:
    """Click on pos[x, y]."""

  @abstractmethod
  def back(self) -> None:
    """Android BACK event."""

  @abstractmethod
  def drag(self, src: tuple[int, int], dst: tuple[int, int]) -> None:
    """Drag from src to dst."""


class ADBControl(ControlInterface):
  """Control device with adb."""

  def adb(self) -> ADB:
    """Dynamically get ADB instance."""
    return ADB("")

  def tap(self, pos: tuple[int, int]) -> None:
    """Click on pos[x, y]."""
    self.adb.click(pos)

  def back(self) -> None:
    """Android BACK event."""
    self.adb.back()

  def drag(self, src: tuple[int, int], dst: tuple[int, int]) -> None:
    """Drag from src to dst."""
    offset_x = src[0] - dst[0]
    offset_y = src[1] - dst[1]
    dist = math.sqrt(abs(offset_x) ** 2 + abs(offset_y) ** 2)
    duration = (dist / 3) * 5 / 1000
    self.adb.swipe(src, dst, duration)


class WIN32Control(ControlInterface):
  """Control device with WIN32 API."""

  def __init__(self, _hwnd: int) -> None:
    """Initialize with window number."""
    self.hwnd = _hwnd
    if self.hwnd is None:
      raise Exception("Need hwnd parameter in WIN32API mode")

  def adb(self) -> ADB:
    """Dynamically get ADB instance."""
    return ADB("")

  def tap(self, pos: tuple[int, int]) -> None:
    """Click on pos[x, y]."""
    click_pos = win32api.MAKELONG(pos[0], pos[1])
    win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, click_pos)
    win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, None, click_pos)

  def back(self) -> None:
    """Android BACK event."""
    # not supported

  def drag_press(self, src: tuple[int, int], dst: tuple[int, int]) -> None:
    """Drag from src[x,y] to dst[x,y]."""
    offset = (dst[0] - src[0], dst[1] - src[1])
    max_value = max(abs(offset[0]), abs(offset[1]))
    max_value = max_value // 5 if max_value > 60 else max_value // 2
    step = (offset[0] / max_value, offset[1] / max_value)

    click_pos = win32api.MAKELONG(src[0], src[1])
    win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, click_pos)

    for i in range(max_value):
      click_pos = win32api.MAKELONG(src[0] + int(step[0] * i), src[1] + int(step[1] * i))
      win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, click_pos)
      time.sleep(0.001)

  def drag_up(self, dst: tuple[int, int]) -> None:
    """Drag up."""
    click_pos = win32api.MAKELONG(dst[0], dst[1])
    win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, click_pos)

  def drag(self, src: tuple[int, int], dst: tuple[int, int]) -> None:
    """Drag from src to dst."""
    self.drag_press(src, dst)
    self.drag_up(dst)
