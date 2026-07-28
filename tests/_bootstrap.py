"""
Подготовка окружения для запуска тестов вне Sublime Text.

Регистрирует в `sys.modules`:
  1. «Облегчённый» пакет `AutoSyntaxByProject` — чтобы работали относительные импорты внутри модулей
    плагина, но не выполнялся настоящий `__init__.py` (он тянет `sublime_plugin/main`, которого нет
    вне Sublime Text).
  2. Заглушки модулей `sublime` и `sublime_plugin` — см. `sublime_stub.py`

Идемпотентно (`sys.modules.setdefault`): безопасно вызывается и из `tests/__init__.py` (запуск как
пакет `tests.X`), и из пролога тест-модуля (запуск отдельных модулей из директории `tests/`).
"""

import os
import sys
import types

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_PKG_DIR = os.path.dirname(_TESTS_DIR)

if _TESTS_DIR not in sys.path:
	sys.path.insert(0, _TESTS_DIR)

import sublime_stub

# Облегчённый пакет плагина: __path__ -> реальная директория, но
# настоящий __init__.py не выполняется.
_pkg = types.ModuleType("AutoSyntaxByProject")
_pkg.__path__ = [_PKG_DIR]
_pkg.__package__ = "AutoSyntaxByProject"
sys.modules.setdefault("AutoSyntaxByProject", _pkg)

# Заглушки sublime / sublime_plugin.
sublime_stub.install()
