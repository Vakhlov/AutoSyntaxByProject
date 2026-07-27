"""
Тестовые двойники (fake) для тест-модулей.

В отличие от `_fixtures` (чистые константы), здесь живут подделки,
зависящие от sublime и модулей плагина. Импортируются тестами после
пролога-бутстрапа (директория `tests/` уже в `sys.path`).
"""

from __future__ import annotations

from typing import Dict, List, Optional, TYPE_CHECKING

from AutoSyntaxByProject.SyntaxApplier import SyntaxApplier
from AutoSyntaxByProject.SyntaxConfigParser import SyntaxConfigParser
from AutoSyntaxByProject.SyntaxPathNormalizer import SyntaxPathNormalizer
from AutoSyntaxByProject.types import SyntaxMap

if TYPE_CHECKING:
	import sublime

_ViewBase = sublime.View if TYPE_CHECKING else object
_WindowBase = sublime.Window if TYPE_CHECKING else object

class _FakeClock():
	"""
	Управляемые часы: модуль `time` плагина подменяется этим объектом.
	"""
	def __init__(self, start: float = 1000.0) -> None:
		self.now = start

	def time(self) -> float:
		return self.now

class _FakeConfigParser(SyntaxConfigParser):
	"""
	SyntaxConfigParser, возвращающий преднастроенный syntax_map.
	"""

	def __init__(self, syntax_map: Optional[SyntaxMap] = None) -> None:
		self._fake_map = syntax_map

	def parse_syntax_map(self, project_data: Optional[Dict]) -> Optional[SyntaxMap]:
		return self._fake_map

class _FakeSyntaxApplier(SyntaxApplier):
	"""
	SyntaxApplier, записывающий вызовы apply_syntax (шпион).
	"""

	def __init__(self, return_value: bool = True) -> None:
		super().__init__(SyntaxPathNormalizer())
		self._return_value = return_value
		self.calls = []

	def apply_syntax(self, view: sublime.View, syntax_path: Optional[str]) -> bool:
		self.calls.append(syntax_path)
		return self._return_value

class _FakeView(_ViewBase):
	"""
	Подделка sublime.View: в тестируемом коде используются методы
	file_name, id и window из sublime.View.
	"""

	def __init__(
		self,
		file_name: Optional[str] = None,
		window: Optional[sublime.Window] = None,
		view_id: int = 1
	) -> None:
		self._file_name = file_name
		self._id = view_id
		self._window = window

	def file_name(self) -> Optional[str]:
		return self._file_name

	def id(self) -> int:
		return self._id

	def window(self) -> Optional[sublime.Window]:
		return self._window

class _FakeWindow(_WindowBase):
	"""
	Подделка sublime.Window: в тестируемом коде используются методы
	`id`, `project_data` и `project_file_name` из `sublime.View.window()`.
	"""

	def __init__(
		self,
		project_file: Optional[str] = None,
		project_data: Optional[dict] = None,
		win_id: int = 1,
		raise_on_data: bool = False,
		views: Optional[List[sublime.View]] = None
	) -> None:
		self._id = win_id
		self._project_data = project_data
		self._project_file = project_file
		self._raise_on_data = raise_on_data
		self._views = views or []
		self.project_data_calls = 0

	def id(self) -> int:
		return self._id

	def project_data(self) -> Optional[dict]:
		self.project_data_calls += 1

		if (self._raise_on_data):
			raise RuntimeError("ошибка project_data")

		return self._project_data

	def project_file_name(self) -> Optional[str]:
		return self._project_file

	def views(self) -> List[sublime.View]:
		return self._views
