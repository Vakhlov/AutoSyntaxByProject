import sublime
from typing import Any, Dict, List, Union

from .types import SettingsDict

# Настройки по умолчанию.
DEFAULT_SETTINGS: SettingsDict = {
	"activated_debounce": 0.5,
	"cache_ttl": 5,
	"debug": False,
	"extension_aliases": {
		"htm": "html",
		"markdown": "md",
		"mdown": "md",
		"mkd": "md"
	},
	"supported_extensions": [".htm", ".html", ".markdown", ".md", ".mdown", ".mkd"]
}

def get_setting(key: str) -> Any:
	"""
	Получает настройку из файла плагина или возвращает значение по умолчанию.

	Значение не кэшируется, чтение происходит при каждом обращении. Поэтому
	изменение файла настроек применяется без перезапуска редактора.

	Args:
		key: Название настройки.

	Returns:
		Значение настройки или None.
	"""
	settings = sublime.load_settings("AutoSyntaxByProject.sublime-settings")

	return settings.get(key, DEFAULT_SETTINGS.get(key))

# Режим отладки.
DEBUG = get_setting('debug')

# Префикс, с которого должен начинаться путь к файлу синтаксиса.
PACKAGES_PREFIX = "Packages/"

# Расширение, которое должен иметь файл синтаксиса.
SYNTAX_EXTENSION = ".sublime-syntax"
