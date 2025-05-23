import logging
import sys
from rich.logging import RichHandler
from rich.console import Console, ConsoleRenderable
from rich.theme import Theme
from rich.text import Text
from typing import Optional

# Custom theme for our logging colors
custom_theme = Theme({"info": "cyan", "warning": "yellow", "error": "red", "debug": "grey70"})

console = Console(theme=custom_theme)


class CustomRichHandler(RichHandler):
	def render(
		self,
		*,
		record: logging.LogRecord,
		message_renderable: "ConsoleRenderable",
		traceback: Optional["ConsoleRenderable"] = None,
	) -> "ConsoleRenderable":
		"""Customize the entire render output based on log level"""
		if record.levelno == logging.DEBUG:
			level = self.get_level_text(record)
			return Text.assemble(level, " ", message_renderable)
		return super().render(
			record=record, message_renderable=message_renderable, traceback=traceback
		)


_DEFAULT_LEVEL = logging.DEBUG

# Cache for loggers to avoid duplicate handlers
_loggers = {}


def get_logger(name: str = "rcpch-guidelines") -> logging.Logger:
	if name in _loggers:
		return _loggers[name]

	logger = logging.getLogger(name)
	logger.setLevel(_DEFAULT_LEVEL)

	if not logger.handlers:
		# Configure rich handler with custom formatting
		rich_handler = CustomRichHandler(
			console=console,
			rich_tracebacks=True,
			tracebacks_show_locals=True,
			omit_repeated_times=True,
			markup=True,
		)
		rich_handler.setLevel(_DEFAULT_LEVEL)
		logger.addHandler(rich_handler)

	logger.propagate = False
	_loggers[name] = logger
	return logger
