import sys
import types

from typing import Any

class _Settings:
	"""
	«Пустые» настройки: get() всегда возвращает default.
	"""
	def get(self, key, default = None):
		return default

class Edit:
	"""
	Заглушка `sublime.Edit` — нужна для разрешения аннотации `edit: sublime.Edit` в
	сигнатуре `AutoSyntaxReapplyCommand.run` при импорте вне Sublime Text.
	"""

class EventListener:
	"""
	Заглушка `sublime_plugin.EventListener` — базовый класс обработчиков событий
	Sublime Text. Нужна, чтобы `class AutoSyntaxByProject(sublime_plugin.EventListener)`
	определился при импорте вне Sublime Text.
	"""

class Settings:
	"""
	Заглушка `sublime.Settings` — нужна, чтобы тестовые подделки настроек могли от неё
	наследоваться (для Pyright) вне Sublime Text.
	"""

class TextCommand:
	"""
	Заглушка `sublime_plugin.TextCommand` — нужна, чтобы команда
	`AutoSyntaxReapplyCommand` определилась при импорте вне Sublime Text.
	"""

	def __init__(self, view: Any) -> None:
		self.view = view

class View:
	"""
	Заглушка `sublime.View`. Нужна только для разрешения аннотаций типов
	(например, `view: sublime.View`) при импорте модулей плагина — реальное
	поведение `view` в тестах обеспечивается отдельными моками.
	"""

class Window:
	"""
	Заглушка `sublime.Window`. Нужна для наследования тестовыми подделками и
	разрешения аннотаций при импорте вне Sublime Text.
	"""

def install() -> None:
	"""
	Регистрирует заглушку в sys.modules. `setdefault` — чтобы не перезаписывать
	настоящий sublime, если тесты вдруг запускаются изнутри Sublime Text.
	"""
	stub: Any = types.ModuleType("sublime")
	stub.load_settings = lambda name: _Settings()
	stub.Edit = Edit
	stub.Settings = Settings
	stub.View = View
	stub.Window = Window
	sys.modules.setdefault("sublime", stub)

	plugin: Any = types.ModuleType("sublime_plugin")
	plugin.EventListener = EventListener
	plugin.TextCommand = TextCommand
	sys.modules.setdefault("sublime_plugin", plugin)
