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

	Args:
		key: Название настройки.

	Returns:
		Значение настройки или None.
	"""
	settings = sublime.load_settings("AutoSyntaxByProject.sublime-settings")

	return settings.get(key, DEFAULT_SETTINGS.get(key))

# Задержка перед повторным вызовом обработчика события `on_activated` в секундах.
ACTIVATED_DEBOUNCE = get_setting('activated_debounce')

# Время жизни кэша данных проекта в секундах.
CACHE_TTL = get_setting('cache_ttl')

# Режим отладки.
DEBUG = get_setting('debug')

# Псевдонимы поддерживаемых расширений файлов.
EXTENSION_ALIASES = get_setting('extension_aliases')

# Префикс, с которого должен начинаться путь к файлу синтаксиса.
PACKAGES_PREFIX = "Packages/"

# Поддерживаемые расширения файлов.
SUPPORTED_EXTENSIONS = set(get_setting('supported_extensions'))

# Расширение, которое должен иметь файл синтаксиса.
SYNTAX_EXTENSION = ".sublime-syntax"
