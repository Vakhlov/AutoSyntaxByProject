"""
Вспомогательные функции для управления логированием в тестах.
"""

import contextlib
import logging

from typing import Iterator

_LOGGER_NAME = "AutoSyntaxByProject.logger"

@contextlib.contextmanager
def muted_logger(
	name: str = _LOGGER_NAME,
	level: int = logging.CRITICAL
) -> Iterator[logging.Logger]:
	"""
	Контекстный менеджер: приглушает логгер `name` до уровня `level` и
	гарантированно восстанавливает исходный уровень при выходе, даже
	если внутри блока возникло исключение.

	Используется либо напрямую через `with`, либо в `unittest` через
	`contextlib.ExitStack` (см. тестовые модули).

	Args:
		name: Имя логгера.
		level: Уровень, до которого приглушается логгер на время блока.
	Yields:
		Приглушённый логгер.
	"""

	logger = logging.getLogger(name)
	original = logger.level
	logger.setLevel(level)

	try:
		yield logger
	finally:
		logger.setLevel(original)
