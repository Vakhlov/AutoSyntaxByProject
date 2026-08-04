import os
import sublime
import sublime_plugin
import time
from typing import Dict, Optional, Tuple

from .constants import get_setting
from .logger import logger
from .SyntaxApplier import SyntaxApplier
from .SyntaxConfigParser import SyntaxConfigParser
from .SyntaxPathNormalizer import SyntaxPathNormalizer

class AutoSyntaxByProject(sublime_plugin.EventListener):
	"""
	Основной класс-обработчик событий Sublime Text.
	Только подписывается на события и координирует работу других классов.
	"""

	# Текущий экземпляр класса для доступа из команд.
	_instance: Optional["AutoSyntaxByProject"] = None

	def __init__(self) -> None:
		# Создаем экземпляры вспомогательных классов.
		self._path_normalizer = SyntaxPathNormalizer()
		self._config_parser = SyntaxConfigParser()
		self._syntax_applier = SyntaxApplier(self._path_normalizer)

		# Кэш данных проекта.
		self._project_cache: Dict[str, Tuple[Optional[Dict], float]] = {}
		self._cache_ttl = get_setting("cache_ttl")

		# Ограничение частоты вызовов `on_activated`.
		self._activated_debounce = get_setting("activated_debounce")
		self._last_activated: Dict[int, float] = {}

		# Запоминаем экземпляр для доступа из команд.
		AutoSyntaxByProject._instance = self

		logger.info("плагин загружен")

	@classmethod
	def instance(cls) -> Optional["AutoSyntaxByProject"]:
		"""
		Возвращает текущий экземпляр обработчика событий или None.
		Используется командами (например, `auto_syntax_reapply`).
		"""
		return cls._instance

	# --- Методы-обработчики событий Sublime Text ---

	def on_activated(self, view: sublime.View) -> None:
		"""
		Срабатывает при переключении на вкладку.
		Ограничивает частоту вызовов, чтобы избежать лишней нагрузки.
		"""
		logger.debug("вызван `on_activated`")

		# 1. Получаем идентификатор представления.
		view_id = view.id()

		# 2. Узнаём, когда функция вызывалась последний раз.
		last_time = self._last_activated.get(view_id, 0)

		# 3. Перечитываем задержку из настроек.
		self._activated_debounce = get_setting("activated_debounce")

		# 4. Если вызывается чаще, чем раз в 0.5 секунды — игнорируем.
		current_time = time.time()

		if current_time - last_time < self._activated_debounce:
			logger.debug(f"слишком частый вызов 'on_activated' для {view_id}, пропускаем")
			return

		# 5. Иначе запоминаем время вызова.
		self._last_activated[view_id] = current_time
		
		# 6. И применяем синтаксис.
		self._apply_syntax_if_needed(view)

	def on_load(self, view: sublime.View) -> None:
		"""
		Срабатывает при загрузке (открытии) файла.
		"""
		logger.debug("вызван `on_load`")

		self._apply_syntax_if_needed(view)

	def on_post_save(self, view: sublime.View) -> None:
		"""
		Срабатывает после сохранения файла.
		Если сохранён файл проекта — повторно применяет синтаксис ко всем
		подходящим вкладкам окна (карта синтаксисов могла измениться).
		"""
		logger.debug("вызван `on_post_save`")

		if self._is_project_file(view):
			self._reapply_window(view)

			return

		self._apply_syntax_if_needed(view)

	# --- Основные методы логики ---

	def _apply_syntax_if_needed(self, view: sublime.View) -> None:
		"""
		Основная логика плагина.
		Проверяет, нужно ли применить синтаксис, и применяет если нужно.
		"""
		logger.debug("вызван _apply_syntax_if_needed")

		# 1. Проверяем, есть ли у `view` имя файла.
		file_path = view.file_name()

		if not file_path:
			logger.debug("у файла нет имени (создан новый и ещё не сохранён), пропускаем")
			return

		# 2. Проверяем расширение файла.
		extension = os.path.splitext(file_path)[1].lower()

		if not self._is_supported_extension(extension):
			logger.debug(f"расширение {extension} не поддерживается, пропускаем")
			return

		# 3. Получаем данные проекта.
		project_data = self._get_project_data(view)

		if not project_data:
			logger.debug("нет данных проекта, пропускаем")
			return

		# 4. Парсим настройки синтаксиса.
		syntax_map = self._config_parser.parse_syntax_map(project_data)

		if not syntax_map:
			logger.debug("нет настроек синтаксисов в проекте, пропускаем")
			return

		# 5. Определяем нужный синтаксис.
		extension_key = self._get_extension_key(extension)

		if not extension_key:
			logger.warning(f"пустой ключ для расширения {extension}; проверьте extension_aliases в настройках")
			return

		if extension_key not in syntax_map:
			logger.debug(f"ключ {extension_key} не найден в настройках проекта")
			return

		target_syntax = syntax_map[extension_key]

		if not target_syntax:
			logger.debug(f"пустой путь к синтаксису для {extension_key}")
			return

		# 6. Применяем синтаксис через SyntaxApplier.
		success = self._syntax_applier.apply_syntax(view, target_syntax)

		if success:
			logger.debug(f"успешно установлен синтаксис {target_syntax} для {os.path.basename(file_path)}")
		else:
			logger.debug(f"не удалось установить синтаксис {target_syntax} для {os.path.basename(file_path)}")

	def _get_project_data(self, view: sublime.View) -> Optional[Dict]:
		"""
		Получает данные проекта.
		"""
		logger.debug("вызван _get_project_data")

		# 1. Получаем окно (`window`) из `view`.
		window = view.window()

		if not window:
			logger.debug("нет окна")
			return None

		# 2. Получаем имя файла проекта.
		project_file = window.project_file_name()

		if not project_file:
			logger.debug("нет файла проекта")
			return None

		# 3. Формируем ключ для кэша.
		cache_key = f"{project_file}_{window.id()}"

		# 4. Проверяем кэш.
		if cache_key in self._project_cache:
			cached_data, timestamp = self._project_cache[cache_key]

			# 5. Если данные есть и не устарели — возвращаем.
			self._cache_ttl = get_setting("cache_ttl")

			if time.time() - timestamp < self._cache_ttl:
				logger.debug("возвращаем данные проекта из кэша")
				return cached_data

		# 6. Иначе загружаем свежие данные.
		logger.debug("загружаем свежие данные проекта")

		try:
			project_data = window.project_data()
		except Exception as e:
			logger.debug(f"ошибка загрузки данных проекта: {e}")
			return None

		# 7. Сохраняем в кэш и возвращаем.
		self._project_cache[cache_key] = (project_data, time.time())

		return project_data

	def _get_extension_key(self, extension: str) -> Optional[str]:
		"""
		Преобразует расширение файла в ключ для поиска в настройках.
		Пример: '.htm' -> 'html', '.markdown' -> 'md'.

		Args:
			extension: Расширение файла с точкой (например, '.htm').

		Returns:
			Ключ для поиска в настройках (например, 'html')
			или None, если расширение не поддерживается.
		"""
		logger.debug("вызван _get_extension_key")

		# 1. Убираем точку из расширения.
		ext_without_dot = extension[1:]

		# 2. Возвращаем либо псевдоним, либо само расширение без точки, если псевдонима нет.
		return get_setting("extension_aliases").get(ext_without_dot, ext_without_dot)

	def _is_project_file(self, view: sublime.View) -> bool:
		"""
		Проверяет, является ли представление (view) файлом `.sublime-project`.
		"""

		file_path = view.file_name()

		return bool(file_path and file_path.endswith(".sublime-project"))

	def _is_supported_extension(self, extension: str) -> bool:
		"""
		Проверяет, поддерживается ли расширение.
		"""
		logger.debug("вызван _is_supported_extension")

		return extension in get_setting("supported_extensions")

	def _reapply_window(self, view: sublime.View) -> None:
		"""
		Сбрасывает кэш проекта и повторно применяет синтаксис ко всем
		представлениям окна, которому принадлежит `view`.
		"""

		window = view.window()

		if not window:
			return

		self._project_cache.clear()

		for current_view in window.views():
			self._apply_syntax_if_needed(current_view)

	def reapply(self, view: sublime.View) -> None:
		"""
		Сбрасывает кэш проекта и заново применяет синтаксис к `view`.
		Используется командой принудительного применения после ручного
		изменения карты синтаксисов в файле проекта.

		Args:
			view: Представление, к которому применяется синтаксис.
		"""

		logger.debug("вызван `reapply`")

		self._project_cache.clear()
		self._apply_syntax_if_needed(view)
