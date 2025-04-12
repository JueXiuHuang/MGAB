import traceback
from abc import ABC, abstractmethod
from ctypes import windll

import cv2
import win32gui
import win32ui
from PIL import Image

from adb import ADB


class Screen(ABC):
  """Define screen related operation."""

  @abstractmethod
  def get_screenshot(self, zoom_ratio: float) -> tuple[bool, Image.Image]:
    """Get screenshot."""


class ADBScreen(Screen):
  """Screen related operation with ADB."""

  def adb() -> ADB:
    """Dynamically get ADB instance."""
    return ADB("")

  def get_screenshot(self, zoom_ratio: float) -> tuple[bool, Image.Image]:
    """Get screenshot."""
    try:
      img = self.adb.screenshot()
      height, width = img.shape[:2]
      img = cv2.resize(img, (int(width * zoom_ratio), int(height * zoom_ratio)))
    except:
      print(traceback.format_exc())
      return (False, None)
    return (True, img)


class WIN32Screen(Screen):
  """Screen related operation with win32 api."""

  def __init__(self, _hwnd: int) -> None:
    self.hwnd = _hwnd
    if self.hwnd is None:
      raise Exception("Need hwnd in WIN32API mode")

  def get_window_size_info(self) -> tuple[int, int, int, int]:
    """Get window size info."""
    left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
    w = right - left
    h = bot - top
    return (left, top, w, h)

  def resize_window(self, size: tuple[int, int]) -> None:
    """Resize window."""
    old_info = self.getWindowSizeInfo()
    w_offset = size[0] - old_info[2]
    h_offset = size[1] - old_info[3]
    win32gui.MoveWindow(self.hwnd, old_info[0] - w_offset // 2, old_info[1] - h_offset // 2, size[0], size[1], True)

  def get_screenshot(self, zoom_ratio: float) -> tuple[bool, Image.Image]:
    """Get screenshot."""
    _, _, w, h = self.getWindowSizeInfo()
    # windows zoom setting
    w = int(w * zoom_ratio)
    h = int(h * zoom_ratio)

    hwnddc = win32gui.GetWindowDC(self.hwnd)
    mfcdc = win32ui.CreateDCFromHandle(hwnddc)
    savedc = mfcdc.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfcdc, w, h)

    savedc.SelectObject(bmp)

    result = windll.user32.PrintWindow(self.hwnd, savedc.GetSafeHdc(), 3)
    print(result)

    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)

    if bmpinfo["bmWidth"] != 1 or bmpinfo["bmHeight"] != 1:
      im = Image.frombuffer("RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1)
    else:
      im = None

    win32gui.DeleteObject(bmp.GetHandle())
    savedc.DeleteDC()
    mfcdc.DeleteDC()
    win32gui.ReleaseDC(self.hwnd, hwnddc)

    return ((im is not None), im)
