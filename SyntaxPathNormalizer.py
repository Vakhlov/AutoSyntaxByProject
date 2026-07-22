from typing import Dict, Optional

from .constants import PACKAGES_PREFIX, SYNTAX_EXTENSION
from .logger import logger

class SyntaxPathNormalizer:
	"""
	Отвечает за нормализацию путей к файлам синтаксисов.
	Кэширует результаты для производительности.
	"""

	def __init__(self):
		# Кэш для хранения нормализованных путей к файлам синтаксисов.
		self._cache: Dict[str, str] = {}

		logger.debug("SyntaxPathNormalizer инициализирован")

	def normalize(self, syntax_path: str) -> Optional[str]:
		"""
		Нормализует путь к синтаксису для сравнения.
		Убирает `Packages/` и `.sublime-syntax` из пути.
		Использует кэш для ускорения.

		Args:
			syntax_path: Путь к файлу синтаксиса или None.

		Returns:
			Нормализованный путь или None.
		"""
		logger.debug(f"нормализация пути: {syntax_path}")

		# 1. Проверяем, что путь указан.
		if not syntax_path:
			logger.debug("не указан путь для нормализации")
			return None

		# 2. Проверяем, есть ли путь в кэше.
		if syntax_path in self._cache:
			# 3. Если есть — возвращаем из кэша.
			logger.debug(f"возвращаем из кэша: {self._cache[syntax_path]}")
			return self._cache[syntax_path]

		# 4. Если нет — нормализуем путь.
		result = syntax_path

		if result.startswith(PACKAGES_PREFIX):
			result = result[len(PACKAGES_PREFIX):]

		if result.endswith(SYNTAX_EXTENSION):
			result = result[:-len(SYNTAX_EXTENSION)]

		# 5. Сохраняем в кэш и возвращаем результат.
		self._cache[syntax_path] = result

		logger.debug(f"результат нормализации: {result}")

		return result
