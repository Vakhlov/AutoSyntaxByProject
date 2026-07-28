import os
import sys

# Подготовка окружения вне Sublime Text до импорта sublime/модулей плагина.
# См. tests/_bootstrap.py. Работает при любом способе запуска тестов.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap

import logging
import unittest

from AutoSyntaxByProject import logger as logger_module
from AutoSyntaxByProject.logger import setup_logger

class TestSetupLogger(unittest.TestCase):
	"""
	Тесты `setup_logger`.

	Важно: `logging.getLogger(name)` — глобальный синглтон по имени на весь процесс.
	Поэтому каждый тест использует уникальное имя (производное от имени метода), а в
	`tearDown` обработчики снимаются — чтобы тест можно было безопасно перезапустить.
	"""

	def setUp(self) -> None:
		self._logger_name = f"TestSetupLogger.{self._testMethodName}"
		self._original_debug = logger_module.DEBUG

	def tearDown(self) -> None:
		# Снимаем обработчики с тестового логгера.
		log = logging.getLogger(self._logger_name)

		for handler in list(log.handlers):
			log.removeHandler(handler)

		# Возвращаем DEBUG
		logger_module.DEBUG = self._original_debug

	def testReturnLogger(self) -> None:
		"""
		Возвращает экземпляр `logging.Logger`.
		"""

		result = setup_logger(self._logger_name)

		self.assertIsInstance(result, logging.Logger)

	def testAddsSingleStreamHandler(self) -> None:
		"""
		При первом вызове добавляется ровно один StreamHandler.
		"""

		log = setup_logger(self._logger_name)

		self.assertEqual(len(log.handlers), 1)
		self.assertIsInstance(log.handlers[0], logging.StreamHandler)

	def testLevelInfoWhenDebugFalse(self) -> None:
		"""
		При DEBUG = False уровень отладки INFO.
		"""

		logger_module.DEBUG = False
		
		log = setup_logger(self._logger_name)

		self.assertEqual(log.level, logging.INFO)

	def testLevelDebugWhenDebugTrue(self) -> None:
		"""
		При DEBUG = True уровень отладки DEBUG.
		"""

		logger_module.DEBUG = True

		log = setup_logger(self._logger_name)

		self.assertEqual(log.level, logging.DEBUG)

	def testPropagateFalse(self) -> None:
		"""
		Логи не передаются родительским логгерам (изоляция).
		"""

		log = setup_logger(self._logger_name)

		self.assertFalse(log.propagate)

	def testFormatterPrefix(self) -> None:
		"""
		Сообщения форматируются с префиксом 'AutoSyntaxByProject'.
		"""

		log = setup_logger(self._logger_name)

		handler = log.handlers[0]
		record = logging.LogRecord(
			name = "test",
			level = logging.INFO,
			pathname = __file__,
			lineno = 1,
			msg = "Hello",
			args = (),
			exc_info = None
		)

		self.assertEqual(handler.format(record), "AutoSyntaxByProject: Hello")

	def testIdempotentNoDuplicateHandlers(self) -> None:
		"""
		Повторный вызов с тем же именем не дублирует обработчики.
		"""

		first = setup_logger(self._logger_name)
		second = setup_logger(self._logger_name)

		self.assertIs(first, second)
		self.assertEqual(len(second.handlers), 1)

if __name__ == '__main__':
	unittest.main()