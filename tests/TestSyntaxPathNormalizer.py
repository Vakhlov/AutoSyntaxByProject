import os
import sys

# Подготовка окружения вне Sublime Text до импорта sublime/модулей плагина.
# См. tests/_bootstrap.py. Работает при любом способе запуска тестов.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap

import unittest

from _fixtures import _DEFAULT_HTML_SYNTAX_PATH
from AutoSyntaxByProject.SyntaxPathNormalizer import SyntaxPathNormalizer

class TestSyntaxPathNormalizer(unittest.TestCase):
	"""
	Тесты для SyntaxPathNormalizer.
	"""

	def setUp(self) -> None:
		"""
		Выполняется перед каждым тестом.
		"""
		self.normalizer = SyntaxPathNormalizer()

	def testNormalizeSimple(self) -> None:
		"""
		Тест: нормализация простого пути.
		"""
		result = self.normalizer.normalize(_DEFAULT_HTML_SYNTAX_PATH)
		self.assertEqual(result, "HTML/HTML")

	def testNormalizeNone(self) -> None:
		"""
		Тест: передача None.
		"""
		result = self.normalizer.normalize(None)
		self.assertIsNone(result)

	def testNormalizeEmpty(self) -> None:
		"""
		Тест: передача пустой строки.
		"""
		result = self.normalizer.normalize("")
		self.assertIsNone(result)

	def testNormalizeWithoutPackages(self) -> None:
		"""
		Тест: путь без префикса `Packages/`.
		"""
		result = self.normalizer.normalize("HTML/HTML.sublime-syntax")
		self.assertEqual(result, "HTML/HTML")

	def testNormalizeWithoutExtension(self) -> None:
		"""
		Тест: путь без расширения `.sublime-syntax`.
		"""
		result = self.normalizer.normalize("Packages/HTML/HTML")
		self.assertEqual(result, "HTML/HTML")

	def testNormalizeCache(self) -> None:
		"""
		Тест: кэширование.
		"""
		path = _DEFAULT_HTML_SYNTAX_PATH
		first = self.normalizer.normalize(path)
		second = self.normalizer.normalize(path)

		# Проверяем, что результат одинаковый.
		self.assertEqual(first, second)

		# Проверяем, что значение есть в кэше.
		self.assertIn(path, self.normalizer._cache)

if __name__ == "__main__":
	unittest.main()