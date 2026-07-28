# AutoSyntaxByProject

![coverage](badges/coverage.svg)

> **Плагин для Sublime Text 4**
> Автоматически применяет синтаксис Liquid для HTML и Markdown файлов в проектах Jekyll.

---

## Кратко

| Вопрос            | Ответ |
|-------------------|-------|
| **Для кого?**     | Разработчики сайтов на Jekyll |
| **Что делает?**   | Автоматически включает подсветку Liquid в `.html` и `.md` файлах |
| **Зачем?**        | Чтобы не переключать синтаксис вручную каждый раз |
| **Что нужно?**    | Sublime Text 4 + пакет [Liquid](https://packagecontrol.io/packages/Liquid) |
| **Как работает?** | Читает настройки из `.sublime-project` |

---

При разработке сайтов на **Jekyll** файлы `.html` и `.md` содержат код Liquid:
```liquid
{% if page.title %}
	<h1>{{ page.title }}</h1>
{% endif %}
```

Стандартные синтаксисы HTML и Markdown **не подсвечивают** Liquid-код. Пакет [Liquid](https://packagecontrol.io/packages/Liquid) добавляет подсветку, но требует **ручного переключения** для каждого файла.

Этот плагин делает переключение автоматическим.

## Возможности

1. Автоматическое применение Liquid-синтаксиса для `.html` и `.md` файлов.
1. Работает только в проектах, где это настроено (не мешает в других проектах).

## Установка

**Важно:** перед использованием установите пакет [Liquid](https://packagecontrol.io/packages/Liquid) — он добавляет подсветку синтаксиса Liquid.

### Вручную

1. Перейдите в директорию `Packages/` Sublime Text:
	- **macOS**: `~/Library/Application Support/Sublime Text/Packages/`
1. Склонируйте репозиторий:
	```bash
	git clone https://github.com/vakhlov/AutoSyntaxByProject.git
	```
1. Перезапустите Sublime Text.

---

## Настройка проекта

В корне вашего Jekyll-проекта создайте или отредактируйте файл `имя-проекта.sublime-project`:

```json
{
	// ...
	"settings": {
		"extensions": {
			"html": "Packages/Liquid/HTML (Liquid).sublime-syntax",
			"md": "Packages/Liquid/Markdown (Liquid).sublime-syntax"
		}
	}
}
```

Теперь все `.html` и `.md` файлы в этом проекте будут автоматически открываться с синтаксисом Liquid.

---

## Настройка плагина

Создайте файл `Packages/User/AutoSyntaxByProject.sublime-settings` со следующими настройками (для переопределения настроек по умолчанию):

```json
{
	// Задержка перед повторным вызовом обработчика события `on_activated` в секундах.
	"activated_debounce": 0.5,

	// Время жизни кэша данных проекта в секундах.
	"cache_ttl": 5,

	// Работа в режиме отладки (true — выводятся подробные логи в консоль).
	"debug": false,

	// Псевдонимы поддерживаемых расширений файлов.
	"extension_aliases": {
		"htm": "html",
		"markdown": "md",
		"mdown": "md",
		"mkd": "md"
	},

	// Поддерживаемые расширения файлов.
	"supported_extensions": [".htm", ".html", ".markdown", ".md", ".mdown", ".mkd"],
}
```

---

## Как это работает

1. Вы открываете файл `.html` или `.md` в вашем Jekyll-проекте.
1. Плагин проверяет настройки в `имя-проекта.sublime-project`.
1. Находит, какой синтаксис указан для открытого файла.
1. Применяет найденный файл синтаксиса.
1. Код Liquid подсвечивается без ручного переключения.

---

## Совместимость

• **Sublime Text:** версия 4 (Build 4100+),
• **Python:** 3.8+ (поставляется в Sublime Text),
• **Зависимость:** пакет [Liquid](https://packagecontrol.io/packages/Liquid) (устанавливается отдельно).

---

## Лицензия

Лицензия MIT. См. файл [license](license)

---

## Благодарности