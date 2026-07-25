#!/usr/bin/env python3

"""
Генерирует SVG-бейдж покрытия из coverage.json.

Использование:
```bash
coverage_badge.py <coverage.json> <out.svg>
```
"""

import json
import os
import sys

def _color(percent: float) -> str:
	"""
	Возвращает цвет бейджа в зависимости от процента покрытия.

	Args:
		percent: Процент покрытия.

	Returns:
		HEX-код цвета: >= 90 — ярко-зелёный, >= 75 — жёлтый,
		>= 50 — оранжевый, иначе — красный.
	"""

	if percent >= 90:
		return "#4CA154" # ярко-зелёный

	if percent >= 75:
		return "#DFB317" # жёлтый

	if percent >= 50:
		return "#FE7D37" # оранжевый

	return "#E05D44" # красный

def _text_width(text: str) -> int:
	"""
	Оценивает ширину текста в пикселях для размещения надписей на бейдже.

	Args:
		text: Текст, ширину которого необходимо оценить.

	Returns:
		Приблизительная ширина в пикселях для шрифта ~11px (Verdana/DejaVu Sans).
	"""

	return int(len(text) * 6.6) + 12

def make_svg(label: str, value: str, color: str) -> str:
	"""
	Собирает SVG-бейдж (в стиле shields.io) из подписи, значения и цвета.

	Args:
		label: Левая подпись бейджа (например, «покрытие»).
		value: Правое значение (например, «98%»).
		color: HEX-код цвета правой части.

	Returns:
		Строка с валидным SVG.
	"""

	label_width, value_width = _text_width(label), _text_width(value)
	width = label_width + value_width

	return (
		f'<svg aria-label="{label}: {value}" height="20" role="img" width="{width}" xmlns="http://www.w3.org/2000/svg">'
		f'<linearGradient id="s" x2="0" y2="100%">'
		f'<stop offset="0" stop-color="#BBB" stop-opacity=".1" />'
		f'<stop offset="1" stop-opacity=".1" />'
		f'</linearGradient>'
		f'<clipPath id="r">'
		f'<rect height="20" rx="3" width="{width}" />'
		f'</clipPath>'
		f'<g clip-path="url(#r)">'
		f'<rect fill="#555" height="20" width="{label_width}"/>'
		f'<rect fill="{color}" height="20" width="{value_width}" x="{label_width}" />'
		f'<rect fill="url(#s)" height="20" width="{width}" />'
		f'</g>'
		f'<text fill="#FFF" font-family="Verdana, DejaVu Sans, Geneva, sans-serif" font-size="11" text-anchor="middle" x="{label_width // 2}" y="14">{label}</text>'
		f'<text fill="#FFF" font-family="Verdana, DejaVu Sans, Geneva, sans-serif" font-size="11" text-anchor="middle" x="{label_width + value_width // 2}" y="14">{value}</text>'
		f'</svg>'
	)

def main() -> None:
	"""
	Читает процент покрытия из coverage.json и создает SVG-бейдж.

	Пути берутся из аргументов командной строки:
		sys.argv[1] — путь к coverage.json.
		sys.argv[2] — путь к выходному SVG.
	"""

	coverage_json, out_svg = sys.argv[1], sys.argv[2]
	data = json.load(open(coverage_json, encoding = "utf-8"))
	percent = float(data["totals"]["percent_covered"])
	svg = make_svg("покрытие", f"{round(percent)}%", _color(percent))

	out_dir = os.path.dirname(out_svg)

	if out_dir:
		os.makedirs(out_dir, exist_ok = True)

	open(out_svg, "w", encoding = "utf-8").write(svg)
	print(f"Бейдж покрытия: {round(percent)}% -> {out_svg}")

if __name__ == "__main__":
	main()
