import logging

from .constants import DEBUG

def setup_logger(name: str = "AutoSyntaxByProject") -> logging.Logger:
	"""
	Создаёт и возвращает изолированный логгер.

	Args:
		name: Имя логгера

	Returns:
		Изолированный логгер с префиксом 'AutoSyntaxByProject:'
	"""

	# 1. Создаём логгер с указанным именем.
	logger = logging.getLogger(name)

	# 2. Проверяем, есть ли уже обработчики.
	if not logger.handlers:
		# 3. Создаём обработчик для вывода в консоль.
		handler = logging.StreamHandler()

		# 4. Настраиваем формат с префиксом.
		formatter = logging.Formatter("AutoSyntaxByProject: %(message)s")
		handler.setFormatter(formatter)

		# 5. Добавляем обработчик к логгеру.
		logger.addHandler(handler)

		# 6. Устанавливаем уровень логирования.
		debug = DEBUG
		logger.setLevel(logging.DEBUG if debug else logging.INFO)

		# 7. Отключаем передачу логов родительским логгерам (для изоляции).
		logger.propagate = False

	return logger

# Создаём экземпляр логгера для использования в других файлах.
logger = setup_logger(__name__)
