"""
Общие тестовые данные для тест-модулей.

Чистые константы без зависимости от sublime/заглушек. Импортируются тестами
после пролога-бутстрапа (директория `tests/` уже в `sys.path`), пожтому доступны и
при запуске как пакет, и как отдельные модули из `tests/`.
"""

# Встроенный синтаксис HTML из дистрибутива Sublime Text.
_DEFAULT_HTML_SYNTAX_PATH = "Packages/HTML/HTML.sublime-syntax"

# Синтаксисы Liquid.
_HTML_SYNTAX_PATH = "Packages/Liquid/HTML (Liquid).sublime-syntax"
_MD_SYNTAX_PATH = "Packages/Liquid/Markdown (Liquid).sublime-syntax"
