import os
import sys

# Подготовка окружения вне Sublime Text до импорта sublime/модулей плагина.
# См. tests/_bootstrap.py. Работает при любом способе запуска тестов.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap

import unittest

from typing import Optional, TYPE_CHECKING

from AutoSyntaxByProject.SyntaxApplier import SyntaxApplier

if TYPE_CHECKING:
	import sublime

# Pyright видит настоящие типы sublime; в runtime это object,
# т.к. sublime недоступен вне Sublime Text.
_SettingsBase = sublime.Settings if TYPE_CHECKING else object
_ViewBase = sublime.View if TYPE_CHECKING else object

class _StubNormalizer:
	"""
	Стаб `SyntaxPathNormalizer`: возвращает преднастроенное значение через
	`mapping`. Позволяет тестам точно управлять результатом нормализации и
	проверять логику сравнения `SyntaxApplier` в изоляции от реального нормализатора.
	"""

	def __init__(self, mapping = None, default = "NORMALIZED"):
		self._mapping = dict(mapping or {})
		self._default = default

	def normalize(self, syntax_path):
		if not syntax_path:
			return None

		return self._mapping.get(syntax_path, self._default)

class _StubSettings(_SettingsBase):
	"""
	Мок `view.settings()`: по ключу `'syntax'` возвращает преднастроенный
	текущий синтаксис, для отсальных ключей — `default`.
	"""

	def __init__(self, current_syntax: Optional[str] = None):
		self._current_syntax = current_syntax

	def get(self, key, default = None):
		if key == "syntax":
			return self._current_syntax

		return default

class _SpyView(_ViewBase):
	"""
	Мок `sublime.View` для тестов.
	Запоминает вызовы `set_syntax_file` и по запросу выбрасывает исключение.
	"""

	def __init__(self, current_syntax: Optional[str] = None, raise_on_set: bool = False):
		self._settings = _StubSettings(current_syntax)
		self._raise_on_set = raise_on_set
		self.set_syntax_file_calls = []

	def settings(self):
		return self._settings

	def set_syntax_file(self, syntax_path):
		if self._raise_on_set:
			raise RuntimeError("ошибка set_syntax_file")

		self.set_syntax_file_calls.append(syntax_path)

# Правильный путь к синтаксису.
_VALID_PATH = "Packages/HTML/HTML.sublime-syntax"

class TestSyntaxApplier(unittest.TestCase):
	"""
	Тесты для SyntaxApplier.
	"""

	# apply_syntax

	def testApplySyntaxSuccess(self):
		"""
		Успех: текущий и целевой синтаксис различаются — синтаксис применяется.
		"""
		
		normalizer = _StubNormalizer(mapping = {_VALID_PATH: "HTML/HTML"})
		view = _SpyView(current_syntax = "Packages/Plain/HTML.sublime-syntax")

		applier = SyntaxApplier(normalizer)

		result = applier.apply_syntax(view, _VALID_PATH)

		self.assertTrue(result)
		self.assertEqual(view.set_syntax_file_calls, [_VALID_PATH])

	def testApplySyntaxAlreadySet(self):
		"""
		Синтаксис уже установлен: `normalize(target) == normalize(current)` —
		повторная установка не выполняется.
		"""

		normalizer = _StubNormalizer(mapping = {_VALID_PATH: "HTML/HTML"})
		view = _SpyView(current_syntax = _VALID_PATH)

		applier = SyntaxApplier(normalizer)

		result = applier.apply_syntax(view, _VALID_PATH)

		self.assertFalse(result)
		self.assertEqual(view.set_syntax_file_calls, [])

	def testApplySyntaxCurrentNone(self):
		"""
		Текущий синтаксис — None: нормализация текущего пропускается,
		целевой синтаксис применяется.
		"""

		normalizer = _StubNormalizer()
		view = _SpyView(current_syntax = None)

		applier = SyntaxApplier(normalizer)

		result = applier.apply_syntax(view, _VALID_PATH)

		self.assertTrue(result)
		self.assertEqual(view.set_syntax_file_calls, [_VALID_PATH])

	def testApplySyntaxInvalidEmpty(self):
		"""
		Пустой путь: применение не происходит.
		"""

		normalizer = _StubNormalizer()
		view = _SpyView()

		applier = SyntaxApplier(normalizer)

		result = applier.apply_syntax(view, "")

		self.assertFalse(result)
		self.assertEqual(view.set_syntax_file_calls, [])

	def testApplySyntaxInvalidNone(self):
		"""
		Путь — None: применение не происходит.
		"""

		normalizer = _StubNormalizer()
		view = _SpyView()

		applier = SyntaxApplier(normalizer)

		result = applier.apply_syntax(view, None)

		self.assertFalse(result)
		self.assertEqual(view.set_syntax_file_calls, [])

	def testApplySyntaxInvalidNoPrefix(self):
		"""
		Путь без префикса `Packages/`: применение не происходит.
		"""

		normalizer = _StubNormalizer()
		view = _SpyView()

		applier = SyntaxApplier(normalizer)

		result = applier.apply_syntax(view, "HTML/HTML.sublime-syntax")

		self.assertFalse(result)
		self.assertEqual(view.set_syntax_file_calls, [])

	def testApplySyntaxInvalidNoExtension(self):
		"""
		Путь без расширения `.sublime-syntax`: применение не происходит.
		"""

		normalizer = _StubNormalizer()
		view = _SpyView()

		applier = SyntaxApplier(normalizer)

		result = applier.apply_syntax(view, "Packages/HTML/HTML")

		self.assertFalse(result)
		self.assertEqual(view.set_syntax_file_calls, [])

	def testApplySyntaxSuppressRaiseOnSetSyntaxError(self):
		"""
		`set_syntax_file` выбрасывает исключение: ошибка подавляется,
		возвращается False.
		"""

		normalizer = _StubNormalizer(mapping = {_VALID_PATH: "HTML/HTML"})
		view = _SpyView(
			current_syntax = "Packages/Plain/HTML.sublime-syntax",
			raise_on_set = True
		)

		applier = SyntaxApplier(normalizer)

		result = applier.apply_syntax(view, _VALID_PATH)

		self.assertFalse(result)

	# _is_valid_syntax_path

	def testIsValidSyntaxPathValid(self):
		"""
		Корректный путь проходит проверку.
		"""

		normalizer = _StubNormalizer()

		applier = SyntaxApplier(normalizer)

		result = applier._is_valid_syntax_path(_VALID_PATH)

		self.assertTrue(result)

	def testIsValidSyntaxPathEmpty(self):
		"""
		Пустой путь не проходит проверку.
		"""

		normalizer = _StubNormalizer()

		applier = SyntaxApplier(normalizer)

		result = applier._is_valid_syntax_path("")

		self.assertFalse(result)

	def testIsValidSyntaxPathNone(self):
		"""
		Путь None не проходит проверку.
		"""

		normalizer = _StubNormalizer()

		applier = SyntaxApplier(normalizer)

		result = applier._is_valid_syntax_path(None)

		self.assertFalse(result)

	def testIsValidSyntaxPathNoPrefix(self):
		"""
		Путь без префикса `Packages/` не проходит проверку.
		"""

		normalizer = _StubNormalizer()

		applier = SyntaxApplier(normalizer)

		result = applier._is_valid_syntax_path("HTML/HTML.sublime-syntax")

		self.assertFalse(result)

	def testIsValidSyntaxPathNoExtension(self):
		"""
		Путь без расширения `.sublime-syntax` не проходит проверку.
		"""

		normalizer = _StubNormalizer()

		applier = SyntaxApplier(normalizer)

		result = applier._is_valid_syntax_path("Packages/HTML/HTML")

		self.assertFalse(result)

if __name__ == "__main__":
	unittest.main()
