"""
Минимальные стабы типов для модуля `sublime_plugin` (Sublime Text 4).
"""

from sublime import Edit, View

class EventListener:
	"""
	Базовый класс обработчиков событий; подклассы переопределяют нужные `on`-методы.
	"""

	def on_activated(self, view: View) -> None: ...
	def on_load(self, view: View) -> None: ...
	def on_post_save(self, view: View) -> None: ...

class TextCommand:
	"""
	Базовый класс текстовых команд. `self.view` — целевое представление,
	`run(edit)` — точка входа, вызываемая Sublime Text.
	"""

	view: View

	def __init__(self, view: View) -> None: ...
	def run(self, edit: Edit) -> None: ...
