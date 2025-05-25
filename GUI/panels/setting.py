import tkinter as tk
from tkinter import ttk
from typing import Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from config import AppConfig


class SettingsPanel:
  frame: ttk.Frame
  config: AppConfig
  setting_vars: dict[tuple[str, str], tk.Variable]

  def __init__(
    self,
    parent_frame: ttk.Frame,
    config: AppConfig,
    setting_vars_ref: dict[tuple[str, str], tk.Variable],
  ) -> None:
    self.frame = ttk.Frame(parent_frame, style="Content.TFrame")
    self.config = config
    self.setting_vars = setting_vars_ref
    self._create_widgets()
    self.frame.pack(expand=True, fill=tk.BOTH)

  def _create_field_widget(
    self,
    parent: ttk.Frame,
    section_name: str,
    key: str,
    value: Any,
    field_info: FieldInfo,
  ) -> tuple[ttk.Label, ttk.Checkbutton | ttk.Entry]:
    """Generate Tkinter widget according to field type."""
    key_label_text = f"{key.replace('_', ' ').capitalize()}:"
    key_label = ttk.Label(parent, text=key_label_text, font=("Microsoft JhengHei UI", 9))

    current_var_key = (section_name, key)
    var: tk.Variable
    widget: ttk.Widget

    field_type = field_info.annotation

    if field_type is bool or isinstance(value, bool):
      var = tk.BooleanVar(value=bool(value if value is not None else False))
      widget = ttk.Checkbutton(parent, variable=var)
    elif field_type is int or isinstance(value, int):
      var = tk.IntVar(value=int(value if value is not None else 0))
      widget = ttk.Entry(parent, textvariable=var, width=50, font=("Microsoft JhengHei UI", 9))
    elif field_type is float or isinstance(value, float):
      var = tk.DoubleVar(value=float(value if value is not None else 0.0))
      widget = ttk.Entry(parent, textvariable=var, width=50, font=("Microsoft JhengHei UI", 9))
    else:
      var = tk.StringVar(value=str(value if value is not None else ""))
      widget = ttk.Entry(parent, textvariable=var, width=50, font=("Microsoft JhengHei UI", 9))

    self.setting_vars[current_var_key] = var
    return key_label, widget

  def _create_widgets(self) -> None:
    settings_notebook = ttk.Notebook(self.frame)
    settings_notebook.pack(expand=True, fill="both", padx=10, pady=10)

    for section_name in self.config.model_fields:
      section_model_instance = getattr(self.config, section_name)

      if isinstance(section_model_instance, BaseModel):
        tab_frame = ttk.Frame(settings_notebook, style="Content.TFrame")
        settings_notebook.add(tab_frame, text=section_name.replace("_", " ").capitalize())

        canvas = tk.Canvas(tab_frame, borderwidth=0, background="white")
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Content.TFrame")

        scrollable_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e, c=canvas, cw=canvas_window: c.itemconfigure(cw, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        for index, (key_name, field_info_obj) in enumerate(section_model_instance.model_fields.items()):
          current_value = getattr(section_model_instance, key_name)

          label_widget, entry_widget = self._create_field_widget(
            scrollable_frame, section_name, key_name, current_value, field_info_obj
          )
          label_widget.grid(row=index, column=0, padx=10, pady=8, sticky="w")
          entry_widget.grid(row=index, column=1, padx=10, pady=8, sticky="ew")

        scrollable_frame.grid_columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
