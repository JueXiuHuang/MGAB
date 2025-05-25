import tkinter as tk
from tkinter import scrolledtext, ttk

from adb import ADB


class HomePanel:
  def __init__(self, parent_frame: ttk.Frame, adb_instance: ADB) -> None:
    self.frame = ttk.Frame(parent_frame, style="Content.TFrame")
    self.adb = adb_instance
    self._create_widgets()
    self.frame.pack(expand=True, fill=tk.BOTH)

  def _create_widgets(self) -> None:
    home_content_frame = ttk.Frame(self.frame, style="Content.TFrame")
    home_content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    # left panel including ranking graph and battle statistics
    left_panel = ttk.Frame(home_content_frame, width=250, style="Content.TFrame")
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
    left_panel.pack_propagate(flag=False)

    # ranking graph
    rank_graph_label_text = ttk.Label(left_panel, text="Ranking", style="Header.TLabel")
    rank_graph_label_text.pack(pady=(5, 5), anchor="center")

    rank_graph_canvas = tk.Canvas(left_panel, width=320, height=180, bg="#f0f0f0", relief="solid", borderwidth=1)
    rank_graph_canvas.pack(pady=5, fill=tk.X)
    rank_graph_canvas.create_line(
      20,
      160,
      70,
      50,
      120,
      120,
      170,
      60,
      220,
      130,
      fill="deepskyblue",
      width=3,
      smooth=True,
    )
    rank_graph_canvas.create_text(115, 20, text="示意圖", font=("Microsoft JhengHei UI", 9), fill="gray")

    # win/loss statistic
    stats_outer_frame = ttk.Frame(left_panel, style="Content.TFrame")
    stats_outer_frame.pack(pady=25, fill=tk.X)

    bordered_stats_frame = ttk.Frame(stats_outer_frame, style="Status.TFrame", padding=15)
    bordered_stats_frame.pack(fill=tk.X)

    win_label = ttk.Label(bordered_stats_frame, text="WIN: XX", style="Status.TLabel")
    win_label.pack(anchor="w", pady=3)
    loss_label = ttk.Label(bordered_stats_frame, text="LOSS: YY", style="Status.TLabel")
    loss_label.pack(anchor="w", pady=3)

    # right panel is console
    right_panel = ttk.Frame(home_content_frame, style="Content.TFrame")
    right_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    console_label = ttk.Label(right_panel, text="Console", style="Header.TLabel")
    console_label.pack(anchor="nw", pady=(0, 5))

    self.console_text = scrolledtext.ScrolledText(
      right_panel,
      wrap=tk.WORD,
      height=10,
      relief="solid",
      borderwidth=1,
      font=("Consolas", 10),
    )
    self.console_text.pack(expand=True, fill=tk.BOTH)
    self.console_text.insert(tk.END, "Display console log here...\n")
    for i in range(5):
      self.console_text.insert(tk.END, f"Example log {i + 1}\n")

    self.console_text.configure(state=tk.DISABLED)
