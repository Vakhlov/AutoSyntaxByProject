import os
import sys

# Подготовка окружения вне Sublime Text до импорта sublime/модулей плагина.
# См. tests/_bootstrap.py. Работает при любом способе запуска тестов.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap

import unittest

from typing import Any, Dict, Optional

from AutoSyntaxByProject.constants import DEFAULT_SETTINGS, get_setting

class _FakeSettings:
	"""
	Подделка объекта настроек `sublime`: `get(key, default)` возвращает значение из
	`values`, если ключ есть, иначе — default. Повторяет семантику `sublime.Settings.get`.
	"""

	def __init__(self, values: Optional[Dict] = None) -> None:
		self._values = dict(values or {})

	def get(self, key, default: Any = None) -> Any:
		return self._values.get(key, default)

class TestGetSetting(unittest.TestCase):
	"""
	Тесты `get_setting`.

	Чтобы проверить обе ветви (значение из файла и значение по умолчанию),
	тест подменяет `sublime.load_settings` управляемым объектом настроек и
	восстанавливает оригинал в `tearDown`.
	"""

	def setUp(self) -> None:
		self._sublime: Any = sys.modules["sublime"]
		self._original_load_settings = self._sublime.load_settings

		self._settings = _FakeSettings()
		self._load_calls = []

		def _load(name: str) -> _FakeSettings:
			self._load_calls.append(name)
			return self._settings

		self._sublime.load_settings = _load

	def tearDown(self) -> None:
		self._sublime.load_settings = self._original_load_settings

	def testReturnsValueFromSettings(self) -> None:
		"""
		Значение из файла настроек приоритетнее значения по умолчанию.
		"""

		self._settings._values["debug"] = True

		self.assertEqual(get_setting("debug"), True)

	def testFallsBackToDefault(self) -> None:
		"""
		Нет значения в файле, возвращается значение по умолчанию (скаляр).
		"""

		self.assertEqual(get_setting("cache_ttl"), DEFAULT_SETTINGS["cache_ttl"])

	def testFallsBackToDefaultDict(self) -> None:
		"""
		Нет значения в файле, возвращается значение по умолчанию (словарь).
		"""

		self.assertEqual(get_setting("extension_aliases"), DEFAULT_SETTINGS["extension_aliases"])

	def testReturnsNoneForUnknownKey(self) -> None:
		"""
		Ключа нет ни в файле, ни в настройках по умолчанию — возвращается None.
		"""

		self.assertIsNone(get_setting("nonexistent_key"))

	def testLoadSettingsCalledWithPluginName(self) -> None:
		"""
		Настройки грузятся по имени файла плагина.
		"""

		get_setting("debug")

		self.assertEqual(self._load_calls, ["AutoSyntaxByProject.sublime-settings"])

if __name__ == "__main__":
	unittest.main()