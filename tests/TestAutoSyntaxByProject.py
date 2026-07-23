from __future__ import annotations

import os
import sys

# Подготовка окружения вне Sublime Text до импорта sublime/модулей плагина.
# См. tests/_bootstrap.py. Работает при любом способе запуска тестов.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap

import logging
import unittest

from typing import Any, Dict, Optional, TYPE_CHECKING

from AutoSyntaxByProject import main as main_module
from AutoSyntaxByProject.main import AutoSyntaxByProject
from AutoSyntaxByProject.SyntaxApplier import SyntaxApplier
from AutoSyntaxByProject.SyntaxConfigParser import SyntaxConfigParser
from AutoSyntaxByProject.SyntaxPathNormalizer import SyntaxPathNormalizer
from AutoSyntaxByProject.types import SyntaxMap

if TYPE_CHECKING:
	import sublime

_ViewBase = sublime.View if TYPE_CHECKING else object
_WindowBase = sublime.Window if TYPE_CHECKING else object

_HTML_SYNTAX_PATH = "Packages/Liquid/HTML (Liquid).sublime-syntax"
_MD_SYNTAX_PATH = "Packages/Liquid/Markdown (Liquid).sublime-syntax"
_PROJECT_DATA = {"settings": {"extensions": {"html": _HTML_SYNTAX_PATH}}}
_PROJECT_FILE = "/project/example.sublime-project"

class _FakeClock():
	"""
	Управляемые часы: модуль `time` плагина подменяется этим объектом.
	"""
	def __init__(self, start: float = 1000.0) -> None:
		self.now = start

	def time(self) -> float:
		return self.now

class _FakeConfigParser(SyntaxConfigParser):
	"""
	SyntaxConfigParser, возвращающий преднастроенный syntax_map.
	"""

	def __init__(self, syntax_map: Optional[SyntaxMap] = None) -> None:
		self._fake_map = syntax_map

	def parse_syntax_map(self, project_data: Optional[Dict]) -> Optional[SyntaxMap]:
		return self._fake_map

class _FakeSyntaxApplier(SyntaxApplier):
	"""
	SyntaxApplier, записывающий вызовы apply_syntax (шпион).
	"""

	def __init__(self, return_value: bool = True) -> None:
		super().__init__(SyntaxPathNormalizer())
		self._return_value = return_value
		self.calls = []

	def apply_syntax(self, view: sublime.View, syntax_path: Optional[str]) -> bool:
		self.calls.append(syntax_path)
		return self._return_value

class _FakeView(_ViewBase):
	"""
	Подделка sublime.View: в тестируемом коде используются методы
	file_name, id и window из sublime.View.
	"""

	def __init__(
		self,
		file_name: Optional[str] = None,
		window: Optional[sublime.Window] = None,
		view_id: int = 1
	) -> None:
		self._file_name = file_name
		self._id = view_id
		self._window = window

	def file_name(self) -> Optional[str]:
		return self._file_name

	def id(self) -> int:
		return self._id

	def window(self) -> Optional[sublime.Window]:
		return self._window

class _FakeWindow(_WindowBase):
	"""
	Подделка sublime.Window: в тестируемом коде используются методы
	`id`, `project_data` и `project_file_name` из `sublime.View.window()`.
	"""

	def __init__(
		self,
		project_file: Optional[str] = None,
		project_data: Optional[dict] = None,
		win_id: int = 1,
		raise_on_data: bool = False
	) -> None:
		self._id = win_id
		self._project_data = project_data
		self._project_file = project_file
		self._raise_on_data = raise_on_data
		self.project_data_calls = 0

	def id(self) -> int:
		return self._id

	def project_data(self) -> Optional[dict]:
		self.project_data_calls += 1

		if (self._raise_on_data):
			raise RuntimeError("ошибка project_data")

		return self._project_data

	def project_file_name(self) -> Optional[str]:
		return self._project_file

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

if __name__ == "__main__":
	unittest.main()
