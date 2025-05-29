import logging
import tkinter as tk
from tkinter import messagebox, ttk

from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined

from adb import ADB
from config import AppConfig

from .panels.home import HomePanel
from .panels.setting import SettingsPanel

logger = logging.getLogger(__name__)


class AppGUI:
  def __init__(self, master: tk.Tk, config: AppConfig, adb: ADB) -> None:
    self.master = master
    master.title("Sample GUI")
    master.geometry("1280x720")

    self.config = config
    self.setting_vars = {}
    self.adb_instance = adb

    self._configure_styles()

    main_container = ttk.Frame(master)
    main_container.pack(expand=True, fill=tk.BOTH)

    # left navigation panel
    self.nav_panel = ttk.Frame(main_container, width=200, style="Nav.TFrame")
    self.nav_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1), pady=0)
    self.nav_panel.pack_propagate(flag=False)

    # content panel
    self.content_panel = ttk.Frame(main_container, style="Content.TFrame")
    self.content_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    self._home_panel_instance = None
    self._settings_panel_instance = None
    self.active_button = None

    self._create_navigation_buttons()

    self.show_home_view()

  def _configure_styles(self) -> None:
    style = ttk.Style()
    style.theme_use("clam")

    # Navigation panel style
    style.configure("Nav.TFrame", background="#e0e0e0")

    # Default (non-selected) navigation button style
    style.configure(
      "Nav.TButton",
      padding=(10, 12),
      font=("Microsoft JhengHei UI", 12),
      relief=tk.FLAT,
      background="#e0e0e0",
      foreground="black",
      borderwidth=0,
      anchor=tk.W,
    )
    style.map("Nav.TButton", background=[("active", "#d0d0d0")])

    # Selected navigation button style
    style.configure(
      "SelectedNav.TButton",
      padding=(10, 12),
      font=("Microsoft JhengHei UI", 12, "bold"),
      relief=tk.FLAT,
      background="#ffffff",
      foreground="black",
      borderwidth=0,
      anchor=tk.W,
    )
    style.map("SelectedNav.TButton", background=[("active", "#f0f0f0")])

    # Content panel style
    style.configure("Content.TFrame", background="white")

    # Other styles
    style.configure("TNotebook.Tab", padding=(10, 5), font=("Microsoft JhengHei UI", 9))
    style.configure("Header.TLabel", font=("Microsoft JhengHei UI", 10, "bold"), background="white")
    style.configure("Status.TFrame", relief="solid", borderwidth=1, background="white")
    style.configure("Status.TLabel", font=("Microsoft JhengHei UI", 10), background="white")

  def _update_nav_button_styles(self, active_button_widget: ttk.Button | None) -> None:
    buttons_to_update = []
    if hasattr(self, "home_button"):
      buttons_to_update.append(self.home_button)
    if hasattr(self, "setting_button"):
      buttons_to_update.append(self.setting_button)

    for btn in buttons_to_update:
      if btn is active_button_widget:
        btn.configure(style="SelectedNav.TButton")
      else:
        btn.configure(style="Nav.TButton")
    self.active_button = active_button_widget

  def _create_navigation_buttons(self) -> None:
    self.home_button = ttk.Button(self.nav_panel, text="HOME", command=self.show_home_view, style="Nav.TButton")
    self.home_button.pack(side=tk.TOP, pady=(15, 0), padx=10, fill=tk.X, ipady=4)

    self.setting_button = ttk.Button(
      self.nav_panel,
      text="Settings",
      command=self.show_setting_view,
      style="Nav.TButton",
    )
    self.setting_button.pack(side=tk.TOP, pady=(0, 15), padx=10, fill=tk.X, ipady=4)

  def _clear_content_panel(self) -> None:
    for widget in self.content_panel.winfo_children():
      widget.pack_forget()

  def show_home_view(self) -> None:
    """Clear panel and display home panel."""
    self._clear_content_panel()
    if not self._home_panel_instance:
      self._home_panel_instance = HomePanel(self.content_panel, self.adb_instance)
    else:
      self._home_panel_instance.frame.pack(expand=True, fill=tk.BOTH)
    self._update_nav_button_styles(self.home_button)

  def show_setting_view(self) -> None:
    """Clear panel and display setting panel."""
    self._clear_content_panel()
    self.setting_vars.clear()
    self._settings_panel_instance = SettingsPanel(self.content_panel, self.config, self.setting_vars)

    save_button_frame = ttk.Frame(self._settings_panel_instance.frame, style="Content.TFrame")
    save_button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 10), padx=10)

    save_button = ttk.Button(save_button_frame, text="Save", command=self.save_settings)
    save_button.pack(side=tk.RIGHT, padx=5)
    self._update_nav_button_styles(self.setting_button)

  def _extract_values_from_ui(self) -> dict:
    """Extract config value from tkinter ui."""
    ui_values = {}
    for (section, key), var in self.setting_vars.items():
      if section not in ui_values:
        ui_values[section] = {}
      try:
        ui_values[section][key] = var.get()
      except tk.TclError:
        default_value_for_fallback = None
        section_model = getattr(self.config, section, None)
        if section_model and hasattr(section_model, key):
          field_info = section_model.model_fields.get(key)
          if field_info and field_info.default is not PydanticUndefined:
            default_value_for_fallback = field_info.default
          else:  # Fallback to current value or basic type default
            current_val = getattr(section_model, key, None)
            if isinstance(current_val, int):
              default_value_for_fallback = 0
            elif isinstance(current_val, float):
              default_value_for_fallback = 0.0
            elif isinstance(current_val, bool):
              default_value_for_fallback = False
            else:
              default_value_for_fallback = ""

        if isinstance(var, tk.IntVar):
          ui_values[section][key] = default_value_for_fallback if isinstance(default_value_for_fallback, int) else 0
        elif isinstance(var, tk.DoubleVar):
          ui_values[section][key] = default_value_for_fallback if isinstance(default_value_for_fallback, float) else 0.0
        elif isinstance(var, tk.BooleanVar):
          ui_values[section][key] = (
            default_value_for_fallback if isinstance(default_value_for_fallback, bool) else False
          )
        else:
          ui_values[section][key] = default_value_for_fallback if isinstance(default_value_for_fallback, str) else ""
    return ui_values

  def _update_internal_config(self, ui_values: dict) -> bool:
    """Update config and validate value type."""
    all_updates_valid = True
    for section_name, section_data in ui_values.items():
      if not hasattr(self.config, section_name):
        continue

      section_model = getattr(self.config, section_name)
      if not isinstance(section_model, BaseModel):
        continue

      for key_name, tk_value in section_data.items():
        if not hasattr(section_model, key_name):
          continue
        try:
          setattr(section_model, key_name, tk_value)
        except ValidationError as e:
          all_updates_valid = False
          error_detail = e.errors()[0]
          err_loc = ".".join(str(loc) for loc in error_detail["loc"])
          messagebox.showerror(
            "Save fail",
            f"Column '{section_name}.{err_loc}' has invalid value [{tk_value}]:\n{error_detail['msg']}",
          )
          logger.exception("Validation error updating %s.%s with '%s': %s", section_name, key_name, tk_value, e)
    return all_updates_valid

  def _write_config_to_file(self) -> None:
    """Write config into file."""
    config_file_path_str = "config.toml"
    try:
      self.config.save_to_file(config_file_path_str)
      messagebox.showinfo("Save Success", f"Config save to {config_file_path_str} success")
      logger.info("Config saved to '%s' successfully.", config_file_path_str)
    except Exception as e:
      error_msg = f"Unexpect error when saving config: {e}"
      logger.exception(error_msg)
      messagebox.showerror("Save fail", error_msg)

  def save_settings(self) -> None:
    """Save config setting on ui to file."""
    ui_values = self._extract_values_from_ui()
    if self._update_internal_config(ui_values):
      self._write_config_to_file()
