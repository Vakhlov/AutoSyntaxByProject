import sublime

from .constants import PACKAGES_PREFIX, SYNTAX_EXTENSION
from .logger import logger
from .SyntaxPathNormalizer import SyntaxPathNormalizer

class SyntaxApplier:
	"""
	Применяет синтаксис к представлению (`view`).
	Проверяет валидность и обрабатывает ошибки.
	"""

	def __init__(self, path_normalizer: SyntaxPathNormalizer):
		"""
		Инициализация с экземпляром нормализатора путей.

		Args:
			path_normalizer: Экземпляр SyntaxPathNormalizer.
		"""

		self._path_normalizer = path_normalizer

	def apply_syntax(self, view: sublime.View, syntax_path: str) -> bool:
		"""
		Применяет синтаксис к `view`.

		Args:
			view: Представление Sublime Text.
			syntax_path: Путь к файлу синтаксиса.

		Return:
			`True` в случае успеха, `False` в случае ошибки.
		"""
		logger.debug(f"попытка применить синтаксис: {syntax_path}")

		# 1. Проверяем валидность пути к синтаксису.
		if not self._is_valid_syntax_path(syntax_path):
			logger.warning(f"неправильный путь к синтаксису: {syntax_path}")
			return False

		# 2. Получаем текущий синтаксис.
		current_syntax = view.settings().get('syntax')

		# 3. Нормализуем оба пути для сравнения.
		target_normalized = self._path_normalizer.normalize(syntax_path)
		current_normalized = self._path_normalizer.normalize(current_syntax) if current_syntax else None

		# 4. Если синтаксис уже установлен — выходим.
		if current_normalized == target_normalized:
			logger.debug("синтаксис уже установлен, пропускам")
			return False

		# 5. Пытаемся установить новый синтаксис.
		try:
			view.set_syntax_file(syntax_path)

			logger.debug(f"установлен синтаксис: {syntax_path}")

			# 6. Возвращаем результат.
			return True
		except Exception as e:
			# 7. Обрабатываем ошибки.
			logger.error(f"ошибка при установке синтаксиса {syntax_path}: {e}")
			return False

	def _is_valid_syntax_path(self, syntax_path: str) -> bool:
		"""
		Проверяет, что путь к синтаксису корректен.

		Args:
			syntax_path: Путь к файлу синтаксиса.

		Returns:
			`True`, если путь правильный, иначе `False`
		"""
		logger.debug("проверяем путь к файлу синтаксиса")

		# 1. Проверяем, что путь не пустой.
		if not syntax_path:
			logger.debug("путь к файлу синтаксиса пустой")
			return False

		# 2. Проверяем, что путь начинается с `Packages/`.
		if not syntax_path.startswith(PACKAGES_PREFIX):
			logger.debug(f"путь к файлу синтаксиса не начинается с '{PACKAGES_PREFIX}': {syntax_path}")
			return False

		# 3. Проверяем, что путь заканчивается на `.sublime-syntax`.
		if not syntax_path.endswith(SYNTAX_EXTENSION):
			logger.debug(f"путь к файлу синтаксиса не заканчивается на '{SYNTAX_EXTENSION}': {syntax_path}")
			return False

		# 4. Возвращаем `True` — проверка пройдена.
		return True
