import re
from typing import Dict, List, Optional

from .logger import logger


class SyntaxConfigParser:
	"""
	Парсит настройки синтаксисов из данных проекта (файл `.sublime-project`).
	Поддерживает два формата:
	1. extensions: {'html': 'Packages/...', 'md': 'Packages/...'}
	2. project_syntaxes: [{'rules': [{'file_name': '*.html'}], 'syntax': '...'}]
	"""

	# Регулярное выражения для проверки расширения файла.
	EXTENSION_PATTERN = re.compile(r'\*\.([a-zA-Z0-9]+)')

	def parse_syntax_map(self, project_data: Dict) -> Optional[Dict[str, str]]:
		"""
		Извлекает маппинг расширений на синтаксисы из настроек проекта.

		Args:
			project_data: Словарь с данными проекта из `window.project_data()`.

		Returns:
			Словарь вида `{'html': 'Packages/...', 'md': 'Packages/'}`
			или None, если настройки не найдены.
		"""
		logger.debug("начинаем разбор настроек синтаксисов")

		# 1. Проверяем, есть ли данные проекта.
		if not project_data:
			logger.debug("нет данных проекта")
			return None

		# 2. Пытаемся получить настройки из секции `settings`.
		settings = project_data.get('settings', {})

		if not settings:
			logger.debug("нет раздела `settings` в данных проекта")
			return None

		# 3. Проверяем формат `extensions`.
		extensions = settings.get('extensions', {})

		if extensions:
			logger.debug(f"найден формат 'extensions' с {len(extensions)} элементами")
			return self._parse_extensions_format(extensions)

		# 4. Проверяем формат `project_syntaxes`.
		project_syntaxes = settings.get('project_syntaxes', [])

		if project_syntaxes:
			logger.debug(f"найден формат 'project_syntaxes' с {len(project_syntaxes)} элементами")
			return self._parse_project_syntaxes_format(project_syntaxes)

		# 5. Ничего не найдено, возвращаем None.
		return None

	def _parse_extensions_format(self, extensions: Dict) -> Dict[str, str]:
		"""
		Парсит формат `extensions`.
		Приводит ключи к нижнему регистру.

		Пример:
			{'HTML': 'Packages/...', 'Md': 'Packages/...'}
			-> {'html': 'Packages/...', 'md': 'Packages/...'}
		"""
		logger.debug("парсим формат 'extensions'")

		# 1. Создаём пустой словарь для результата.
		result = {}

		# 2. Проходим по всем ключам и значениям.
		for key, value in extensions.items():
			# 3. Приводим ключи к нижнему регистру.
			normalized_key = key.lower()
			result[normalized_key] = value
			logger.debug(f"добавлено: {normalized_key} -> {value}")

		# 4. Возвращаем результат.
		return result

	def _parse_project_syntaxes_format(self, project_syntaxes: List) -> Dict[str, str]:
		"""
		Парсит формат `project_syntaxes` (совместимость с ApplySyntax).
		Извлекает расширения файлов из правил.

		Пример:
			[{
				'rules': [{'file_name': '*.html'}],
				'syntax': 'Packages/HTML/HTML.sublime-syntax'
			}]
			-> {'html': 'Packages/HTML/HTML.sublime-syntax'}
		"""
		logger.debug("парсим формат 'project_syntaxes'")

		# 1. Создаем пустой словарь для результата.
		result = {}

		# 2. Проходим по всем правилам.
		for rule in project_syntaxes:
			# 3. Для каждого правила проверяем наличие синтаксиса.
			syntax = rule.get('syntax')

			if not syntax:
				logger.debug("пропускаем правило без 'syntax'")
				continue

			# 4. Получаем список правил.
			rules = rule.get('rules', [])

			if not rules:
				logger.debug("пропускаем правило без 'rules'")
				continue

			# 5. Ищем расширение в паттерне `file_name`.
			for r in rules:
				file_name_pattern = r.get('file_name')

				if not file_name_pattern:
					continue

				# Ищем расширение в паттерне с помощью регулярного выражения
				match = self.EXTENSION_PATTERN.search(file_name_pattern)

				if match:
					# Извлекаем расширение без звёздочки и точки.
					ext = match.group(1).lower()

					# 6. Добавляем в словарь.
					result[ext] = syntax

					logger.debug(f"добавлено: {ext} -> {syntax}")
					break # Выходим из внутреннего цикла, т.к. синтаксис уже найден.

		# 7. Возвращаем результат.
		return result
