from __future__ import annotations

import os
import sys

# Подготовка окружения вне Sublime Text до импорта sublime/модулей плагина.
# См. tests/_bootstrap.py. Работает при любом способе запуска тестов.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap

import logging
import unittest

import sublime # Заглушка (см. _bootstrap) — нужна для констрирования `Edit`.

from _fakes import _FakeConfigParser, _FakeSyntaxApplier, _FakeView, _FakeWindow
from _fixtures import _HTML_SYNTAX_PATH, _PROJECT_DATA, _PROJECT_FILE
from AutoSyntaxByProject.main import AutoSyntaxByProject
from AutoSyntaxByProject.AutoSyntaxReapplyCommand import AutoSyntaxReapplyCommand

class TestAutoSyntaxReapplyCommand(unittest.TestCase):
	"""
	Тесты AutoSyntaxReapplyCommand.
	"""

	def setUp(self) -> None:
		# Приглушаем логгер плагина, чтобы не забивать вывод при создании экземпляра.
		self._logger = logging.getLogger("AutoSyntaxByProject.logger")
		self._original_level = self._logger.level
		self._logger.setLevel(logging.CRITICAL)
		
		# Плагин с подмененными зависимостями.
		self._plugin = AutoSyntaxByProject()
		self._config_parser = _FakeConfigParser()
		self._syntax_applier = _FakeSyntaxApplier()
		self._plugin._config_parser = self._config_parser
		self._plugin._syntax_applier = self._syntax_applier

	def tearDown(self) -> None:
		self._logger.setLevel(self._original_level)

	# run

	def testRunAppliesSyntaxToCurrentView(self) -> None:
		"""
		`run` вызывает AutoSyntaxByProject.reapply (а тот применяет
		синтаксис к текущему представлению).
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.htm", window = window, view_id = 1)

		cmd = AutoSyntaxReapplyCommand(view)

		cmd.run(sublime.Edit())

		self.assertEqual(self._syntax_applier.calls, [_HTML_SYNTAX_PATH])

	def testRunWithoutListenerIsSafe(self) -> None:
		"""
		Если обработчик не инициализирован, `run` безопасно завершается без вызовов.
		"""

		AutoSyntaxByProject._instance = None

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.htm", window = window, view_id = 1)

		cmd = AutoSyntaxReapplyCommand(view)

		cmd.run(sublime.Edit())

		self.assertEqual(self._syntax_applier.calls, [])
