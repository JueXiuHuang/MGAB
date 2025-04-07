from enum import IntEnum


class ControlMode(IntEnum):
  WIN32API = 0
  ADB = 1


class Emulator(IntEnum):
  BLUESTACKS = 0
  NOX = 1


class ExtractMode(IntEnum):
  LEFTTOP = 0
  CENTER = 1


class Status(IntEnum):
  LOBBY = 0
  WAIT = 1
  GAME = 2
  FINISH = 3
  TROPHY = 4
  FINISH_ANIMATION = 5
  ARCADE = 6


class ADBMode(IntEnum):
  IP = 0
  ID = 1
