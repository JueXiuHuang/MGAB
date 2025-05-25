import tkinter as tk

from adb import ADB
from config import AppConfig
from GUI.app import AppGUI

if __name__ == "__main__":
  config = AppConfig.load_from_file("config.toml")
  adb = ADB(config.general.package)
  root = tk.Tk()
  app = AppGUI(root, config, adb)
  root.mainloop()
