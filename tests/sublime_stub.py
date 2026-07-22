import sys
import types

class _Settings:
	"""
	«Пустые» настройки: get() всегда возвращает default.
	"""
	def get(self, key, default = None):
		return default

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

def install():
	"""
	Регистрирует заглушку в sys.modules. `setdefault` — чтобы не перезаписывать
	настоящий sublime, если тесты вдруг запускаются изнутри Sublime Text.
	"""
	stub = types.ModuleType("sublime")
	stub.load_settings = lambda name: _Settings()
	stub.Settings = Settings
	stub.View = View
	stub.Window = Window
	sys.modules.setdefault("sublime", stub)

	plugin = types.ModuleType("sublime_plugin")
	plugin.EventListener = EventListener
	sys.modules.setdefault("sublime_plugin", plugin)
