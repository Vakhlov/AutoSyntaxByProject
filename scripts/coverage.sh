#!/usr/bin/env bash

# Локальный прогон тестов с покрытием и генерация SVG-бейджа.
#
# Запуск: `bash scripts/coverage.sh`
# (после `chmod +x scripts/coverage.sh` - `./scripts/coverage.sh`)
# Переопределить интерпретатор: `PYTHON=python3.11 bash scripts/coverage.sh`
#
# Использует `venv .venv` (создается автоматически): системный Python от Homebrew
# "externally managed" (PEP 668) и запрещает `pip install` напрямую; в `venv` работает
# даже если команды `coverage`/`pip` не в PATH.

# Строгий режим bash:
# -e: выход из скрипта при первой ошибке;
# -u: обращение к неопределённым переменным — ошибка;
# -o pipefail: при падении в конвейере выполнение завершается.
set -euo pipefail

PYTHON="${PYTHON:-python3}"
VENV="${VENV:-.venv}"

# Переходим в корень репозитория.
cd "$(dirname "$0")/.."

# Создаём venv, если его ещё нет.
if [ ! -d "$VENV" ]; then
	echo "Создаю виртуальное окружение $VENV..."
	"$PYTHON" -m venv "$VENV"
fi

# Активируем venv (только внутри скрипта).
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# Ставим `coverage`, если его ещё нет.
if ! python -m coverage --version > /dev/null 2>&1; then
	echo "coverage не найден, устанавливаю..."
	python -m pip install coverage
fi

# Тесты с покрытием.
coverage run -m unittest discover -s tests -t . -p 'Test*.py'

# Текстовый отчет + JSON (нужен бейджу).
coverage report
coverage json

# SVG-бейдж.
python scripts/coverage_badge.py coverage.json badges/coverage.svg

echo "badges/coverage.svg обновлён."