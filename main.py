import tomllib
from pathlib import Path

from adb import ADB

if __name__ == "__main__":
  with Path("sample config.toml").open("rb") as f:
    data = tomllib.load(f)
  adb = ADB(data["general"]["package"])
