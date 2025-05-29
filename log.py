import logging
import queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

log_queue = queue.Queue()


def setup_logger(gui_log_handler_enabled: bool) -> tuple[logging.Logger, queue.Queue]:
  """Set up root logger."""
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  logger.handlers.clear()

  console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(console_formatter)
  logger.addHandler(console_handler)

  if gui_log_handler_enabled:
    from logging.handlers import QueueHandler

    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)

  return logger, log_queue


class LogDisplayManager:
  """A log display manager."""

  def __init__(self, text_widget: ScrolledText, log_queue: queue.Queue, update_interval: int = 100) -> None:
    self.text_widget = text_widget
    self.log_queue = log_queue
    self.update_interval = update_interval
    self.is_running = True
    self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    self.text_widget.config(state=tk.DISABLED)

    self._schedule_log_check()

  def _schedule_log_check(self) -> None:
    if self.is_running:
      self._process_pending_logs()
      self.text_widget.after(self.update_interval, self._schedule_log_check)

  def _process_pending_logs(self) -> None:
    processed_count = 0
    max_process_per_cycle = 10

    try:
      while processed_count < max_process_per_cycle:
        try:
          record = self.log_queue.get_nowait()
          self._append_log_record(record)
          processed_count += 1
        except queue.Empty:
          break
    except Exception as e:
      print(f"Error processing logs: {e}")

  def _append_log_record(self, record: logging.LogRecord) -> None:
    try:
      formatted_message = self.formatter.format(record)

      self.text_widget.config(state=tk.NORMAL)
      self.text_widget.insert(tk.END, formatted_message + "\n")
      self.text_widget.see(tk.END)

      self._limit_text_lines()

      self.text_widget.config(state=tk.DISABLED)

    except Exception as e:
      print(f"Error appending log: {e}")

  def _limit_text_lines(self, max_lines: int = 1000) -> None:
    content = self.text_widget.get("1.0", tk.END)
    lines = content.split("\n")

    if len(lines) > max_lines:
      lines_to_delete = len(lines) - max_lines
      self.text_widget.delete("1.0", f"{lines_to_delete}.0")

  def stop(self) -> None:
    """Stop log processing."""
    self.is_running = False

  def add_manual_message(self, message: str, level: str = "INFO") -> None:
    """Add log manually."""
    record = logging.LogRecord(
      name="Manual",
      level=getattr(logging, level.upper(), logging.INFO),
      pathname="",
      lineno=0,
      msg=message,
      args=(),
      exc_info=None,
    )
    self._append_log_record(record)
