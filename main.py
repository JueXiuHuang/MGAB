import tkinter as tk

from adb import ADB
from config import AppConfig
from GUI.app import AppGUI
from log import setup_logger

if __name__ == "__main__":
  logger, log_queue = setup_logger(gui_log_handler_enabled=True)
  config = AppConfig.load_from_file("config.toml")
  adb = ADB(config.general.package)
  root = tk.Tk()
  app = AppGUI(root, config, adb)
  root.mainloop()
