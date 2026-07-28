from __future__ import annotations

import os
import sys

# Подготовка окружения вне Sublime Text до импорта sublime/модулей плагина.
# См. tests/_bootstrap.py. Работает при любом способе запуска тестов.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap

import logging
import unittest

from _log_helpers import muted_logger

_LOGGER_NAME = "muted.logger"

class TestLoggerHelpers(unittest.TestCase):
	"""
	Тесты контекстного менеджера приглушённого логгера?
	"""

	# muted_logger

	def testMutesInsideAndRestoresAfter(self) -> None:
		"""
		Внутри блока логгер приглушён, после — исходный уровень восстановлен.
		"""

		logger = logging.getLogger(_LOGGER_NAME)
		logger.setLevel(logging.DEBUG)

		with muted_logger(_LOGGER_NAME) as muted:
			self.assertIs(muted, logger)
			self.assertEqual(logger.level, logging.CRITICAL)

		self.assertEqual(logger.level, logging.DEBUG)

	def testRestoresOnException(self) -> None:
		"""
		Уровень восстанавливается при исключении внутри блока.
		"""

		logger = logging.getLogger(_LOGGER_NAME)
		logger.setLevel(logging.INFO)

		class _ExceptionForLogger(Exception):
			pass

		with self.assertRaises(_ExceptionForLogger):
			with muted_logger(_LOGGER_NAME):
				raise _ExceptionForLogger()

		self.assertEqual(logger.level, logging.INFO)

	def testAcceptsCustomLevel(self) -> None:
		"""
		Уровень приглушения задаётся аргументом `level`.
		"""

		logger = logging.getLogger(_LOGGER_NAME)
		logger.setLevel(logging.DEBUG)

		with muted_logger(name = _LOGGER_NAME, level = logging.ERROR):
			self.assertEqual(logger.level, logging.ERROR)

	def testIsolatesByName(self) -> None:
		"""
		Приглушение логгера не затрагивает прочие логгеры.
		"""

		otherLogger = logging.getLogger(_LOGGER_NAME + ".other")
		otherLogger.setLevel(logging.DEBUG)

		with muted_logger(_LOGGER_NAME):
			# Логгер плагина приглушён до `CRITICAL`, а
			# otherLogger — до `DEBUG`.
			self.assertEqual(otherLogger.level, logging.DEBUG)

if __name__ == "__main__":
	unittest.main()
