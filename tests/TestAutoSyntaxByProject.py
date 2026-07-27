from __future__ import annotations

import os
import sys

# Подготовка окружения вне Sublime Text до импорта sublime/модулей плагина.
# См. tests/_bootstrap.py. Работает при любом способе запуска тестов.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap

import logging
import unittest

from typing import Any

from _fakes import _FakeClock, _FakeConfigParser, _FakeSyntaxApplier, _FakeView, _FakeWindow
from _fixtures import _HTML_SYNTAX_PATH, _MD_SYNTAX_PATH, _PROJECT_DATA, _PROJECT_FILE
from AutoSyntaxByProject import main as main_module
from AutoSyntaxByProject.main import AutoSyntaxByProject

class TestAutoSyntaxByProject(unittest.TestCase):
	"""
	Тесты AutoSyntaxByProject.
	"""

	def setUp(self) -> None:
		# Приглушаем логгер плагина, чтобы не забивать вывод при создании экземпляра.
		self._logger = logging.getLogger("AutoSyntaxByProject.logger")
		self._original_level = self._logger.level
		self._logger.setLevel(logging.CRITICAL)

		# Управляемые часы.
		self._clock = _FakeClock()
		self._main: Any = main_module
		self._original_time = self._main.time
		self._main.time = self._clock

		# Плагин с подмененными зависимостями.
		self._plugin = AutoSyntaxByProject()
		self._config_parser = _FakeConfigParser()
		self._syntax_applier = _FakeSyntaxApplier()
		self._plugin._config_parser = self._config_parser
		self._plugin._syntax_applier = self._syntax_applier

	def tearDown(self) -> None:
		self._main.time = self._original_time
		self._logger.setLevel(self._original_level)

	# _is_supported_extension

	def testIsSupportedExtensionHtml(self) -> None:
		"""
		`.html` поддерживается.
		"""

		self.assertTrue(self._plugin._is_supported_extension(".html"))

	def testIsSupportedExtensionTxt(self) -> None:
		"""
		`.txt` не поддерживается.
		"""

		self.assertFalse(self._plugin._is_supported_extension(".txt"))

	def testIsSupportedExtensionDoesNotLowerCase(self) -> None:
		"""
		Метод сам не приводит к нижнему регистру — это задача вызывающего.
		"""

		self.assertFalse(self._plugin._is_supported_extension(".HTML"))

	# _get_extension_key

	def testGetExtensionKeyAlias(self) -> None:
		"""
		Возвращает псевдоним расширения в качестве ключа,
		если для этого расширения настроен псевдоним.
		"""

		self.assertEqual(self._plugin._get_extension_key(".htm"), "html")

	def testGetExtensionKeyNoAlias(self) -> None:
		"""
		Возвращает само расширение без точки в качестве ключа,
		если для этого расширения не настроен песевдоним.
		"""

		self.assertEqual(self._plugin._get_extension_key(".extension"), "extension")

	# _get_project_data

	def testGetProjectDataNoWindow(self) -> None:
		"""
		Возвращает None, если нет окна.
		"""

		view = _FakeView(file_name = "/x.html", window = None)

		self.assertIsNone(self._plugin._get_project_data(view))

	def testGetProjectDataNoProjectFile(self) -> None:
		"""
		Возвращает None, если нет файла проекта (`.sublime-project`).
		"""

		window = _FakeWindow(project_file = None, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/x.html", window = window)

		self.assertIsNone(self._plugin._get_project_data(view))

	def testGetProjectDataLoadsAndCaches(self) -> None:
		"""
		Первый вызов загружает данные и кэширует их,
		второй вызов возвращает данные из кэша.
		"""

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/x.html", window = window)

		first = self._plugin._get_project_data(view)
		second = self._plugin._get_project_data(view)

		self.assertEqual(first, _PROJECT_DATA)
		self.assertEqual(second, _PROJECT_DATA)
		self.assertEqual(window.project_data_calls, 1)

	def testGetProjectDataRefreshAfterTTL(self) -> None:
		"""
		После истечения TTL данные загружаются заново.
		"""

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/x.html", window = window)

		self._plugin._get_project_data(view)
		self._clock.now += self._plugin._cache_ttl + 1
		self._plugin._get_project_data(view)

		self.assertEqual(window.project_data_calls, 2)

	def testGetProjectDataHandlesException(self) -> None:
		"""
		Возвращает None, если `window.project_data()` выбрасывает исключение.
		"""

		window = _FakeWindow(project_file = _PROJECT_FILE, raise_on_data = True)
		view = _FakeView(file_name = "/x.html", window = window)

		self.assertIsNone(self._plugin._get_project_data(view))

	# _apply_syntax_if_needed

	def testApplySyntaxIfNeededNoFileName(self) -> None:
		"""
		Не применяет синтаксис, если у view нет имени файла.
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = None, window = window)

		self._plugin._apply_syntax_if_needed(view)

		self.assertEqual(self._syntax_applier.calls, [])

	def testApplySyntaxIfNeededUnsupportedExtension(self) -> None:
		"""
		Не применяет синтаксис, если расширение файла не поддерживается.
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/file.extension", window = window)

		self._plugin._apply_syntax_if_needed(view)

		self.assertEqual(self._syntax_applier.calls, [])

	def testApplySyntaxIfNeededNoWindow(self) -> None:
		"""
		Не применяет синтаксис, если нет окна (и потому нет данных проекта).
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		view = _FakeView(file_name = "/page.html", window = None)

		self._plugin._apply_syntax_if_needed(view)

		self.assertEqual(self._syntax_applier.calls, [])

	def testApplySyntaxIfNeededNoSyntaxMap(self) -> None:
		"""
		Не применяет синтаксис, если в проекте нет настроек синтаксисов.
		"""

		self._config_parser._fake_map = None

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.html", window = window, view_id = 1)

		self._plugin._apply_syntax_if_needed(view)

		self.assertEqual(self._syntax_applier.calls, [])

	def testApplySyntaxIfNeededNoKeyInMap(self) -> None:
		"""
		Не применяет синтаксис к файлу с поддерживаемым расширением, если
		расширение не указано в настройках.
		"""

		self._config_parser._fake_map = {"md": _MD_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.html", window = window, view_id = 1)

		self._plugin._apply_syntax_if_needed(view)

		self.assertEqual(self._syntax_applier.calls, [])

	def testApplySyntaxIfNeededEmptyTarget(self) -> None:
		"""
		Не применяет синтаксис к файлу, если целевой синтаксис пустой.
		"""

		self._config_parser._fake_map = {"html": ""}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.html", window = window, view_id = 1)

		self._plugin._apply_syntax_if_needed(view)

		self.assertEqual(self._syntax_applier.calls, [])

	def testApplySyntaxIfNeededApplies(self) -> None:
		"""
		Применяет синтаксис, если расширение поддерживается, есть окно, настройки, синтаксис.
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.html", window = window, view_id = 1)

		self._plugin._apply_syntax_if_needed(view)

		self.assertEqual(self._syntax_applier.calls, [_HTML_SYNTAX_PATH])

	def testApplySyntaxIfNeededAliasExtension(self) -> None:
		"""
		Применяет синтаксис к файлу, если для его расширения существует псевдоним в настройках.
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.htm", window = window, view_id = 1)

		self._plugin._apply_syntax_if_needed(view)

		self.assertEqual(self._syntax_applier.calls, [_HTML_SYNTAX_PATH])

	# _is_project_file

	def testIsProjectFileTrue(self) -> None:
		"""
		Файл `.sublime-project` распознаётся как файл проекта.
		"""

		view = _FakeView(file_name = _PROJECT_FILE)

		self.assertTrue(self._plugin._is_project_file(view))

	def testIsProjectFileFalse(self) -> None:
		"""
		Обычный файл не распознаётся как файл проекта.
		"""

		view = _FakeView(file_name = "/page.htm")

		self.assertFalse(self._plugin._is_project_file(view))

	def testIsProjectFileNoName(self) -> None:
		"""
		Представление без имени файла не считается файлом проекта.
		"""

		view = _FakeView(file_name = None)

		self.assertFalse(self._plugin._is_project_file(view))

	# reapply

	def testReapplyClearsCacheAndApplies(self) -> None:
		"""
		`reapply` сбрасывает кэш проекта (заставляя перечитать
		данные) и применяет синтаксис к представлению.
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.htm", window = window, view_id = 1)

		# Первый вызов — кэш пуст, данные читаются из «окна».
		self._plugin._get_project_data(view)
		self.assertEqual(window.project_data_calls, 1)

		# Повторный вызов в пределах TTL — используется кэш, перечитывания нет.
		self._plugin._get_project_data(view)
		self.assertEqual(window.project_data_calls, 1)

		# `reapply` сбрасывает кэш и применяет синтаксис; данные перечитываются.
		self._plugin.reapply(view)

		self.assertEqual(window.project_data_calls, 2)
		self.assertEqual(self._syntax_applier.calls, [_HTML_SYNTAX_PATH])

	# события

	def testOnActivatedDebounce(self) -> None:
		"""
		Событие on_activated обрабатывается не чаще, чем указано в настройках.
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.htm", window = window, view_id = 1)

		self._plugin.on_activated(view)
		self.assertEqual(len(self._syntax_applier.calls), 1)

		# В пределах debounce — пропуск.
		self._clock.now += self._plugin._activated_debounce / 2
		self._plugin.on_activated(view)
		self.assertEqual(len(self._syntax_applier.calls), 1)

		# После истечения debounce — снова применяется.
		self._clock.now += self._plugin._activated_debounce + 0.5
		self._plugin.on_activated(view)
		self.assertEqual(len(self._syntax_applier.calls), 2)

	def testOnLoadApplies(self) -> None:
		"""
		Применяет синтаксис при обработке события on_load (к только что открытому файлу).
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.htm", window = window, view_id = 1)

		self._plugin.on_load(view)

		self.assertEqual(self._syntax_applier.calls, [_HTML_SYNTAX_PATH])

	def testOnPostSaveApplies(self) -> None:
		"""
		Применяет синтаксис при обработке события on_post_save (к только что сохраненному файлу).
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		window = _FakeWindow(project_file = _PROJECT_FILE, project_data = _PROJECT_DATA)
		view = _FakeView(file_name = "/page.htm", window = window, view_id = 1)

		self._plugin.on_post_save(view)

		self.assertEqual(self._syntax_applier.calls, [_HTML_SYNTAX_PATH])

	def testOnPostSaveProjectFileReappliesAllViews(self) -> None:
		"""
		Сохранение `.sublime-project` повторно применяет синтаксис ко всем
		подходящим вкладкам окна (карта синтаксисов могла измениться).
		"""

		self._config_parser._fake_map = {"html": _HTML_SYNTAX_PATH}

		view1 = _FakeView(file_name = "/a.htm", view_id = 1)
		view2 = _FakeView(file_name = "/b.htm", view_id = 2)

		window = _FakeWindow(
			project_file = _PROJECT_FILE,
			project_data = _PROJECT_DATA,
			views = [view1, view2]
		)

		view1._window = window
		view2._window = window

		project_view = _FakeView(file_name = _PROJECT_FILE, window = window, view_id = 3)

		self._plugin.on_post_save(project_view)

		self.assertEqual(self._syntax_applier.calls, [_HTML_SYNTAX_PATH, _HTML_SYNTAX_PATH])

if __name__ == "__main__":
	unittest.main()
