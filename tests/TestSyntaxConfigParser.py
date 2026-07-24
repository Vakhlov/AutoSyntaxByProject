import os
import sys

# Подготовка окружения вне Sublime Text до импорта sublime/модулей плагина.
# См. tests/_bootstrap.py. Работает при любом способе запуска тестов.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap

import unittest

from _fixtures import _HTML_SYNTAX_PATH, _MD_SYNTAX_PATH
from AutoSyntaxByProject.SyntaxConfigParser import SyntaxConfigParser

class TestSyntaxConfigParser(unittest.TestCase):
	"""
	Тесты SyntaxConfigParser.
	"""

	def setUp(self) -> None:
		self.parser = SyntaxConfigParser()

	# parse_syntax_map

	def testParseSyntaxMapNone(self) -> None:
		"""
		Нет файла данных проекта, функция возвращает None.
		"""

		result = self.parser.parse_syntax_map(None)

		self.assertIsNone(result)

	def testParseSyntaxMapEmpty(self) -> None:
		"""
		Пустой словарь проекта (проект не настроен), функция возвращает None.
		"""

		result = self.parser.parse_syntax_map({})

		self.assertIsNone(result)

	def testParseSyntaxMapNoSettings(self) -> None:
		"""
		В данных проекта нет настройки 'settings', функция возвращает None.
		"""

		result = self.parser.parse_syntax_map({"foo": "bar"})

		self.assertIsNone(result)

	def testParseSyntaxMapEmptySettings(self) -> None:
		"""
		В данных проекта настройка 'settings' пустая, функция возвращает None.
		"""

		result = self.parser.parse_syntax_map({"settings": {}})

		self.assertIsNone(result)

	def testParseSettingsMapNeitherFormat(self) -> None:
		"""
		В данных проекта настройка 'settings' не содержит раздлелов'extensions' или
		'project_syntaxes', функция возвращает None.
		"""

		project_data = {"settings": {"foo": "bar"}}

		result = self.parser.parse_syntax_map(project_data)

		self.assertIsNone(result)

	def testParseSyntaxMapExtensionsFormat(self) -> None:
		"""
		Формат 'extensions': ключи переводятся к нижнему регистру.
		"""

		project_data = {
			"settings": {
				"extensions": {
					"HTML": _HTML_SYNTAX_PATH,
					"MD": _MD_SYNTAX_PATH
				}
			}
		}

		expected = {
			"html": _HTML_SYNTAX_PATH,
			"md": _MD_SYNTAX_PATH
		}

		result = self.parser.parse_syntax_map(project_data)

		self.assertEqual(result, expected)

	def testParseSyntaxMapProjectSyntaxesFormat(self) -> None:
		"""
		Формат 'project_syntaxes': расширение извлекается из '*.ext'.
		"""

		project_data = {
			"settings": {
				"project_syntaxes": [{
					"rules": [{"file_name": "*.html"}],
					"syntax": _HTML_SYNTAX_PATH
				}]
			}
		}

		expected = {"html": _HTML_SYNTAX_PATH}

		result = self.parser.parse_syntax_map(project_data)

		self.assertEqual(result, expected)

	def testParseSyntaxMapExtensionsPriority(self) -> None:
		"""
		Если заданы оба формата, приоритет за 'extensions'.
		"""

		project_data = {
			"settings": {
				"extensions": {
					"HTML": _HTML_SYNTAX_PATH
				},
				"project_syntaxes": [{
					"rules": [{"file_name": "*.md"}],
					"syntax": _MD_SYNTAX_PATH
				}]
			}
		}

		expected = {"html": _HTML_SYNTAX_PATH}

		result = self.parser.parse_syntax_map(project_data)

		self.assertEqual(result, expected)

	# _parse_extensions_format

	def testParseExtensionsLowcasesKeys(self) -> None:
		"""
		Ключи приводятся к нижнему регистру, значения не меняются.
		"""

		expected = {"html": _HTML_SYNTAX_PATH, "md": _MD_SYNTAX_PATH}

		result = self.parser._parse_extensions_format({"HTML": _HTML_SYNTAX_PATH, "Md": _MD_SYNTAX_PATH})

		self.assertEqual(result, expected)

	# _parse_project_syntaxes_format

	def testParseProjectSyntaxesSkipsNoSyntax(self) -> None:
		"""
		Правило без 'syntax' пропускается.
		"""

		project_syntaxes = [{"rules": [{"file_name": "*.html"}]}]

		result = self.parser._parse_project_syntaxes_format(project_syntaxes)

		self.assertEqual(result, {})

	def testParseProjectSyntaxesSkipsNoRules(self) -> None:
		"""
		Правило без 'rules' пропускается
		"""

		project_syntaxes = [{"syntax": _HTML_SYNTAX_PATH}]

		result = self.parser._parse_project_syntaxes_format(project_syntaxes)

		self.assertEqual(result, {})

	def testParseProjectSyntaxesExtractsExtension(self) -> None:
		"""
		Расширение извлекается из паттерна '*.html'.
		"""

		expected = {"html": _HTML_SYNTAX_PATH}

		project_syntaxes = [{
			"rules": [{"file_name": "*.html"}],
			"syntax": _HTML_SYNTAX_PATH
		}]

		result = self.parser._parse_project_syntaxes_format(project_syntaxes)

		self.assertEqual(result, expected)

	def testParseProjectSyntaxesLowercasesExtension(self) -> None:
		"""
		Расширение из '*.HTML' переводится к нижнему регистру.
		"""

		expected = {"html": _HTML_SYNTAX_PATH}

		project_syntaxes = [{
			"rules": [{"file_name": "*.HTML"}],
			"syntax": _HTML_SYNTAX_PATH
		}]

		result = self.parser._parse_project_syntaxes_format(project_syntaxes)

		self.assertEqual(result, expected)

	def testParseProjectSyntaxesSkipsEntryWithoutFileName(self) -> None:
		"""
		Элемент 'rules' без ключа 'file_name' пропускается, обработка продолжается.
		"""

		expected = {"html": _HTML_SYNTAX_PATH}

		project_syntaxes = [{
			"rules": [{"name": "нет ключа 'file_name'"}, {"file_name": "*.html"}],
			"syntax": _HTML_SYNTAX_PATH
		}]

		result = self.parser._parse_project_syntaxes_format(project_syntaxes)

		self.assertEqual(result, expected)

	def testParseProjectSyntaxesBreaksAfterFirstMatch(self) -> None:
		"""
		Внутри одного правила берётся только первое совпавшее расширение.
		"""

		expected = {"html": _HTML_SYNTAX_PATH}

		project_syntaxes = [{
			"rules": [{"file_name": "*.html"}, {"file_name": "*.md"}],
			"syntax": _HTML_SYNTAX_PATH
		}]

		result = self.parser._parse_project_syntaxes_format(project_syntaxes)

		self.assertEqual(result, expected)

	def testParseProjectSyntaxesMultipleRules(self) -> None:
		"""
		Несколько независимых правил собираются в один словарь.
		"""

		expected = {
			"html": _HTML_SYNTAX_PATH,
			"md": _MD_SYNTAX_PATH
		}

		project_syntaxes = [{
			"rules": [{"file_name": "*.html"}],
			"syntax": _HTML_SYNTAX_PATH
		}, {
			"rules": [{"file_name": "*.md"}],
			"syntax": _MD_SYNTAX_PATH
		}]

		result = self.parser._parse_project_syntaxes_format(project_syntaxes)

		self.assertEqual(result, expected)

if __name__ == "__main__":
	unittest.main()
