"""
Минимальные стабы типов для модуля `sublime_plugin` (Sublime Text 4).
"""

from sublime import View

class EventListener:
	"""
	Базовый класс обработчиков событий; подклассы переопределяют нужные `on`-методы.
	"""

	def on_activated(self, view: View) -> None: ...
	def on_load(self, view: View) -> None: ...
	def on_post_save(self, view: View) -> None: ...
