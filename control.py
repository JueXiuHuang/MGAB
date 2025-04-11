import math
import time

import win32api
import win32con

from adb import ADB
from mode import ControlMode


class Control:
  """Define basic control method for a game.

  Please inherit this class and implement detail control methods for the game.
  """

  def __init__(self, _mode: ControlMode, _hwnd: int | None = None) -> None:
    """Initialize a control object with mode & window number."""
    self.mode = _mode
    if self.mode == ControlMode.WIN32API:
      self.hwnd = _hwnd
      if self.hwnd is None:
        raise Exception("Need hwnd parameter in WIN32API mode")
    elif self.mode == ControlMode.ADB:
      pass

  def adb(self) -> ADB:
    """Dynamically get ADB instance."""
    return ADB("")

  def tap(self, pos: tuple[int, int]) -> None:
    """Click on pos[x, y]."""
    if self.mode == ControlMode.WIN32API:
      click_pos = win32api.MAKELONG(pos[0], pos[1])
      win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, click_pos)
      win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, None, click_pos)
    elif self.mode == ControlMode.ADB:
      self.adb.click(pos)

  def drag_press(self, src: tuple[int, int], dst: tuple[int, int]) -> None:
    """Drag from src[x,y] to dst[x,y]."""
    offset = (dst[0] - src[0], dst[1] - src[1])
    max_value = max(abs(offset[0]), abs(offset[1]))
    max_value = max_value // 5 if max_value > 60 else max_value // 2
    step = (offset[0] / max_value, offset[1] / max_value)

    if self.mode == ControlMode.WIN32API:
      click_pos = win32api.MAKELONG(src[0], src[1])
      win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, click_pos)

      for i in range(max_value):
        click_pos = win32api.MAKELONG(src[0] + int(step[0] * i), src[1] + int(step[1] * i))
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, click_pos)
        time.sleep(0.001)
    elif self.mode == ControlMode.ADB:
      action_down = 0
      action_move = 2

      self.adb.touch(src, action_down)
      for i in range(max_value + 1):
        x = src[0] + int(step[0] * i)
        y = src[1] + int(step[1] * i)
        self.adb.touch((x, y), action_move)
        time.sleep(0.001)

  def drag_up(self, dst: tuple[int, int]) -> None:
    """Drag up."""
    if self.mode == ControlMode.WIN32API:
      click_pos = win32api.MAKELONG(dst[0], dst[1])
      win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, click_pos)
    elif self.mode == ControlMode.ADB:
      pass

  def drag(self, src: tuple[int, int], dst: tuple[int, int]) -> None:
    """Drag from src to dst."""
    if self.mode == ControlMode.WIN32API:
      self.drag_press(src, dst)
      self.drag_up(dst)
    elif self.mode == ControlMode.ADB:
      offset_x = src[0] - dst[0]
      offset_y = src[1] - dst[1]
      dist = math.sqrt(abs(offset_x) ** 2 + abs(offset_y) ** 2)
      duration = (dist / 3) * 5 / 1000
      self.adb.swipe(src, dst, duration)

  def back(self) -> None:
    """Press back button."""
    if self.mode == ControlMode.WIN32API:
      pass  # not supported
    elif self.mode == ControlMode.ADB:
      self.adb.back()
