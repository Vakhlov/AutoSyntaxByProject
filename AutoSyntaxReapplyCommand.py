import sublime
import sublime_plugin

from .logger import logger
from .main import AutoSyntaxByProject

class AutoSyntaxReapplyCommand(sublime_plugin.TextCommand):
	"""
	Принудительно применяет синтаксис к текущему представлению.
	Удобно при изменении карты синтаксисов в файле `.sublime-project`.
	"""

	def run(self, edit: sublime.Edit) -> None:
		listener = AutoSyntaxByProject.instance()

		if listener is None:
			logger.warning("обработчик AutoSyntaxByProject не инициализирован")
			return

		listener.reapply(self.view)
