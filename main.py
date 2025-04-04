import tomllib

from adb import ADB

if __name__ == "__main__":
  with open("sample config.toml", "rb") as f:
    data = tomllib.load(f)
  adb = ADB(data['general']['package'])

  