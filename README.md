ФИО студента: Лимонов Никита Андреевич
Группа студента: ЭФБО-08-24

# Сервис планирования киносъёмок

## Назначение

Приложение предназначено для планирования и организации процесса киносъёмок. Сервис позволяет структурировать информацию о фильмах, их сценах, назначенных съёмках и локациях, а также отслеживать готовность съёмочного процесса и доступность локаций на нужные даты.

## Целевая аудитория

Режиссёры, ассистенты режиссёра, продюсеры и администраторы съёмочного процесса, которым необходимо планировать съёмки, контролировать занятость локаций и отслеживать статус готовности сцен.

## Предметная область

Организация киносъёмочного процесса: фильм состоит из набора сцен, каждая сцена привязывается к конкретной съёмке, которая проводится на определённой локации в назначенную дату.

## Основные сущности

- Фильм
- Сцена
- Съёмка
- Локация

## Используемые технологии

- Python 3.11;
- Django 5.2 — веб-фреймворк;
- Django Template Language (DTL) — шаблоны страниц;
- HTML5, CSS3, JavaScript — разметка, собственное оформление и поведение интерфейса;
- Bootstrap 5.3 — базовая вёрстка;
- SQLite 3, язык SQL и модуль `sqlite3` — база данных веб-интерфейса;
- JSON — исходные данные и хранилище консольной версии;
- pytest — автоматизированные тесты;
- flake8 — проверка качества кода.

## Возможности

Веб-интерфейс (ПР5–ПР7: данные из SQLite, страницы формируются Django-шаблонами):

- главная страница со сводкой (фильмы, локации, активные съёмки), ближайшими съёмками и навигацией;
- список фильмов (с числом сцен) и страница фильма со сценами и его съёмками;
- список локаций (по убыванию вместимости) с подбором по размеру группы (`?capacity=N`) и страница локации;
- проверка занятости локации на любую дату (`/locations/<id>/?date=ГГГГ-ММ-ДД`);
- поиск локаций, свободных на дату и вмещающих группу (`/locations/free/?date=…&crew=N`);
- статистика: итоги по съёмкам, загрузка локаций, самые загруженные локации (порог `?min=N`), съёмки по месяцам, сцены и размер групп по фильмам, сцены без назначенной съёмки;
- график съёмок со статусами (активна / прошла / отменена), кнопка «Скрыть отменённые» (JavaScript) и страница отдельной съёмки;
- собственная страница ошибки 404, ответ 404 для несуществующих объектов.

Консольная версия (`main.py`, сохранена с ПР2–ПР3):

- просмотр, поиск и добавление локаций, подбор локаций по размеру группы;
- просмотр и добавление фильмов и их сцен;
- проверка доступности локации на дату;
- назначение съёмки с проверкой вместимости и запретом двойного бронирования;
- отмена съёмки (съёмка остаётся в истории и перестаёт блокировать локацию);
- график съёмок с количеством дней до каждой;
- справка по классам и функциям (интроспекция);
- хранение данных между запусками в JSON-файлах.

## Объектная модель

Все сущности с идентификатором наследуются от базового класса `Entity` (`models/base.py`), который задаёт поле `id` и метод `to_data()`. Каждый наследник переопределяет `to_data()` (полиморфизм), поэтому `storage.py` сохраняет любые сущности одной функцией `save_entities()`.

### Location — локация (`models/locations.py`)

- атрибуты: `id`, `name`, `address`, `capacity` (вместимость, чел.);
- методы: `is_suitable_for(crew_size)` — вмещает ли группу; `__str__()`;
  `@staticmethod validate_capacity()`; `@classmethod from_data()`; `to_data()`.

### Film — фильм и Scene — сцена (`models/films.py`)

- `Film`: `id`, `title`, `director`, `scenes` (список объектов `Scene`);
  методы `add_scene()`, `get_scene(number)`, `from_data()`, `to_data()`, `__str__()`;
- `Scene`: `number`, `description`, `crew_size` (нужный размер группы);
  сцена существует только внутри фильма (композиция).

### Shooting — съёмка (`models/shootings.py`)

- атрибуты: `id`, `film` → `Film`, `scene` → `Scene`, `location` → `Location`,
  `shooting_date` (`date`), `is_cancelled`;
- `is_cancelled` — свойство только для чтения (инкапсуляция: внутреннее поле `_is_cancelled` меняется лишь методом `cancel()`);
- `status` (`@property`) — текстовый статус с учётом отмены и даты;
- методы: `cancel()`, `days_until()`, `to_data()`, `__str__()`.

### Взаимодействие объектов

```text
Film ──(scenes)──> Scene
  ^                  ^
  └──── Shooting ────┘
          │
          └──> Location
```

Съёмка хранит ссылки на объекты фильма, сцены и локации (`shooting.location.name`, `shooting.film.title`). В JSON вместо объектов записываются идентификаторы `film_id`, `scene_number`, `location_id`; при загрузке `storage.load_shootings()` находит по ним объекты и восстанавливает связи. Записи с несуществующими связями пропускаются.

## Страницы веб-интерфейса

| URL | Имя маршрута | view-функция | Шаблон |
|---|---|---|---|
| `/` | `homepage:index` | `homepage.views.index` | `homepage/index.html` |
| `/films/` | `films:list` | `films.views.films` | `films/film_list.html` |
| `/films/<int:film_id>/` | `films:detail` | `films.views.film_detail` | `films/film_detail.html` |
| `/locations/` | `locations:list` | `locations.views.locations` | `locations/location_list.html` |
| `/locations/<int:location_id>/` | `locations:detail` | `locations.views.location_detail` | `locations/location_detail.html` |
| `/locations/free/` | `locations:free` | `locations.views.free_locations` | `locations/free_locations.html` |
| `/shootings/` | `shootings:list` | `shootings.views.shootings` | `shootings/shooting_list.html` |
| `/shootings/statistics/` | `shootings:statistics` | `shootings.views.statistics` | `shootings/statistics.html` |
| `/shootings/<int:shooting_id>/` | `shootings:detail` | `shootings.views.shooting_detail` | `shootings/shooting_detail.html` |

Если объект не найден, view передаёт в шаблон `None`, шаблон выводит сообщение «… не найден» через `{% if %}/{% else %}`, а ответ получает код 404 (`render(..., status=404)`). Для неизвестных адресов при `DEBUG = False` показывается собственная страница `homepage/404.html` (`handler404 = "homepage.views.page_not_found"`).

Представления только подготавливают данные и вызывают `render(request, шаблон, context)`. HTML в Python-коде не формируется, функция `page()` из ПР5 удалена.

## Django Template Language

### Базовый шаблон и наследование

`templates/base.html` (каталог шаблонов уровня проекта, подключён в `settings.py` через `TEMPLATES["DIRS"] = [BASE_DIR / "templates"]`) содержит общую структуру страницы: `DOCTYPE`, `<head>`, Bootstrap, собственный CSS, навигацию, подвал и подключение JavaScript. Дочерние шаблоны начинаются с `{% extends "base.html" %}` и переопределяют блоки:

- `{% block title %}` — заголовок вкладки;
- `{% block content %}` — содержимое страницы.

### Включаемые шаблоны (`{% include %}`)

| Фрагмент | Где используется |
|---|---|
| `templates/includes/navigation.html` | `base.html` — меню на всех страницах |
| `films/includes/film_card.html` | список фильмов |
| `locations/includes/location_row.html` | таблица локаций |
| `shootings/includes/shooting_status.html` | бейдж статуса съёмки — график, карточка съёмки, списки съёмок |
| `shootings/includes/shooting_item.html` | строка съёмки — главная, страница фильма, страница локации |

### Контекст, циклы и условия

Данные передаются словарём `context`, например в `films.views.films`:

```python
context = {"films": queries.get_films()}
return render(request, "films/film_list.html", context)
```

В шаблоне: `{% for film in films %} … {% empty %} Фильмов нет. {% endfor %}`. Условия `{% if %}/{% elif %}/{% else %}` выбирают статус съёмки (`shooting.is_cancelled`, `shooting.days_until < 0`), занятость локации (`available`), сообщение об отсутствии объекта, активный пункт меню.

### Фильтры

- `{{ films|length }}`, `{{ scenes|length }}` — количество элементов;
- `{{ film.director|default:"не указан" }}` — значение по умолчанию (в базе `director` может быть `NULL`);
- `{{ shooting.shooting_date|date:"d.m.Y" }}` — форматирование даты (строка `ГГГГ-ММ-ДД` из SQLite превращается в `date` в `db/queries.py`);
- `{{ min_capacity|default_if_none:'' }}` — пустое поле формы, если фильтр не задан.

Фильтры отвечают только за представление данных, бизнес-логика (статус съёмки, занятость локации) остаётся в Python (`models/`) и SQL (`db/queries.py`).

### Именованные URL и пространства имён

В `urls.py` каждого приложения задан `app_name` (`homepage`, `films`, `locations`, `shootings`), маршруты названы `list` и `detail`. Ссылки в шаблонах строятся тегом `{% url %}`: `{% url 'films:list' %}`, `{% url 'shootings:detail' shooting.id %}`. Жёстко прописанных адресов в шаблонах нет.

### Статические файлы

Каталог `homepage/static/homepage/`, подключение через `{% load static %}` и `{% static '…' %}`:

| Файл | Назначение |
|---|---|
| `css/style.css` | собственное оформление: шапка с акцентной полосой, карточки `kp-card`, статусы `kp-status-*`, подвал |
| `js/main.js` | текущий год в подвале, кнопка «Скрыть отменённые» на графике съёмок |
| `img/logo.png` | логотип (хлопушка) в навигации |

Проверка: `python manage.py findstatic homepage/img/logo.png`.

## База данных SQLite (ПР7)

Веб-интерфейс читает данные из файла `data/kinoplan.sqlite` средствами стандартного модуля `sqlite3`. Django ORM не используется: SQL-запросы написаны вручную.

### Таблицы

```text
films ──< scenes ──< shootings >── locations
```

| Таблица | Поле | Тип | Ограничения |
|---|---|---|---|
| `films` | `id` | INTEGER | PRIMARY KEY |
| | `title` | TEXT | NOT NULL |
| | `director` | TEXT | может быть NULL |
| `scenes` | `id` | INTEGER | PRIMARY KEY |
| | `film_id` | INTEGER | NOT NULL, FOREIGN KEY → `films.id` |
| | `number` | INTEGER | NOT NULL, UNIQUE вместе с `film_id` |
| | `description` | TEXT | NOT NULL |
| | `crew_size` | INTEGER | NOT NULL, CHECK > 0 |
| `locations` | `id` | INTEGER | PRIMARY KEY |
| | `name` | TEXT | NOT NULL |
| | `address` | TEXT | может быть NULL |
| | `capacity` | INTEGER | NOT NULL, CHECK > 0 |
| `shootings` | `id` | INTEGER | PRIMARY KEY |
| | `scene_id` | INTEGER | NOT NULL, FOREIGN KEY → `scenes.id` |
| | `location_id` | INTEGER | NOT NULL, FOREIGN KEY → `locations.id` |
| | `shooting_date` | TEXT | NOT NULL, формат `ГГГГ-ММ-ДД` |
| | `is_cancelled` | INTEGER | NOT NULL, DEFAULT 0, CHECK IN (0, 1) |

- В JSON сцены вложены в фильм; в базе это отдельная таблица `scenes` со ссылкой `film_id`. Съёмка ссылается на конкретную сцену (`scene_id`), фильм находится через сцену.
- Частичный уникальный индекс `idx_shootings_location_date (location_id, shooting_date) WHERE is_cancelled = 0` запрещает две активные съёмки на одной локации в один день. Правило из ПР2–ПР3 теперь проверяет и сама база.
- `db/database.py → get_connection()` при каждом подключении включает `PRAGMA foreign_keys = ON` (без этого SQLite не проверяет внешние ключи) и `row_factory = sqlite3.Row` (доступ к полям по имени: `row["title"]`, `{{ film.title }}`).

### Файлы

| Файл | Назначение |
|---|---|
| `sql/schema.sql` | `CREATE TABLE IF NOT EXISTS …`: таблицы, ключи, ограничения, индекс |
| `sql/queries.sql` | 25 проверенных в SQLite CLI запросов с комментариями (выборка, WHERE, JOIN, агрегаты, GROUP BY, HAVING) |
| `db/database.py` | подключение, создание схемы, `fetch_all()`/`fetch_one()` |
| `db/import_json.py` | перенос данных из `data/*.json` в базу (`executemany`, параметры `?`, `commit`/`rollback`) |
| `db/queries.py` | запросы веб-интерфейса — функции, которые вызывают Django-представления |
| `data/kinoplan.sqlite` | файл базы данных |

Импорт читает JSON функциями `storage.py`, поэтому записи проходят ту же проверку, что и в консольной версии. Скрипт можно запускать повторно: схема создаётся с `IF NOT EXISTS`, старые записи удаляются, всё выполняется одной транзакцией. Порядок вставки задаётся внешними ключами: фильмы и сцены, затем локации, затем съёмки. `scene_id` для съёмки находит подзапрос по паре `(film_id, number)`.

### Где запросы используются на сайте

| Страница | Запросы `db/queries.py` | Приёмы SQL |
|---|---|---|
| главная | `get_summary`, `get_upcoming_shootings` | COUNT в подзапросах; JOIN + WHERE + LIMIT |
| `/films/` | `get_films` | LEFT JOIN + GROUP BY + COUNT |
| `/films/<id>/` | `get_film`, `get_scenes`, `get_film_shootings` | WHERE; JOIN |
| `/locations/` | `get_locations(min_capacity)` | WHERE capacity >= ? + ORDER BY |
| `/locations/<id>/` | `get_location`, `is_location_busy`, `get_location_shootings` | WHERE; COUNT; JOIN |
| `/locations/free/` | `find_free_locations(date, crew)` | подзапрос NOT IN |
| `/shootings/` | `get_shootings` | JOIN четырёх таблиц |
| `/shootings/<id>/` | `get_shooting` | JOIN + WHERE |
| `/shootings/statistics/` | `get_shooting_totals`, `get_location_statistics`, `get_film_statistics`, `get_busy_locations(min)`, `get_shootings_by_month`, `get_unscheduled_scenes` | COUNT/MIN/MAX/AVG/SUM; LEFT JOIN + GROUP BY; HAVING; LEFT JOIN + IS NULL |

Все значения от пользователя (id из URL, дата, размер группы, порог) передаются только параметрами `?`, например:

```python
fetch_all("""
    SELECT id, name, address, capacity
    FROM locations
    WHERE capacity >= ?
      AND id NOT IN (SELECT location_id FROM shootings
                     WHERE shooting_date = ? AND is_cancelled = 0)
    ORDER BY capacity, name
""", [crew_size, check_date.isoformat()])
```

Статус съёмки («Съёмка отменена», «Съёмка уже прошла», «До съёмки осталось N дн.») считают функции ПР1 `get_days_until_shooting()` и `get_status_text()` из `models/shootings.py`, общие для объектов и строк из базы.

## Структура проекта

```text
film_scheduler/
├── README.md
├── requirements.txt
├── pytest.ini, .flake8   — настройки инструментов
├── manage.py             — управление Django-проектом
├── main.py               — консольная версия приложения
├── storage.py            — JSON ↔ объекты
├── utils.py              — безопасный ввод чисел, дат и строк
├── sql/
│   ├── schema.sql        — создание таблиц
│   └── queries.sql       — SQL-запросы проекта
├── db/                   — работа с SQLite (sqlite3)
│   ├── __init__.py
│   ├── database.py       — подключение, PRAGMA, row_factory
│   ├── import_json.py    — перенос JSON → SQLite
│   └── queries.py        — запросы для представлений
├── kinoplan/             — конфигурация Django-проекта
│   ├── settings.py
│   ├── urls.py           — корневые маршруты, handler404
│   ├── asgi.py
│   └── wsgi.py
├── templates/            — шаблоны уровня проекта
│   ├── base.html
│   └── includes/navigation.html
├── homepage/             — главная страница и страница 404
│   ├── static/homepage/  — css/style.css, js/main.js, img/logo.png
│   └── templates/homepage/  — index.html, 404.html
├── films/                — страницы фильмов
│   └── templates/films/  — film_list.html, film_detail.html,
│                           includes/film_card.html
├── locations/            — страницы локаций
│   └── templates/locations/  — location_list.html, location_detail.html,
│                               free_locations.html,
│                               includes/location_row.html
├── shootings/            — страницы съёмок
│   └── templates/shootings/  — shooting_list.html, shooting_detail.html,
│                               statistics.html,
│                               includes/shooting_status.html,
│                               includes/shooting_item.html
├── models/               — классы предметной области (ПР3)
│   ├── __init__.py
│   ├── base.py           — Entity
│   ├── locations.py      — Location и функции коллекции локаций
│   ├── films.py          — Film, Scene и функции коллекции фильмов
│   └── shootings.py      — Shooting и функции графика съёмок
├── data/
│   ├── locations.json    — исходные данные (JSON)
│   ├── films.json
│   ├── shootings.json
│   └── kinoplan.sqlite   — база данных SQLite
├── report/               — отчёты по практическим работам
└── tests/
    ├── conftest.py       — настройка Django и временной тестовой базы
    ├── test_locations.py
    ├── test_films.py
    ├── test_shootings.py
    ├── test_storage.py
    ├── test_views.py     — тесты веб-страниц и шаблонов
    └── test_database.py  — тесты схемы, импорта, SQL-запросов
```

Каталог пакета `models/` (классы ПР3) не следует путать с файлами `models.py` Django-приложений: они пока пустые, Django-модели появятся при переходе на ORM.

Веб-интерфейс получает данные из SQLite через `db/`, консольная версия `main.py` по-прежнему работает с JSON через `storage.py`. Django ORM, модели Django и формы Django пока не используются.

## Формат данных

`data/locations.json`:

```json
{"id": 1, "name": "Вокзал, павильон 3", "address": "ул. Каланчёвская, 2", "capacity": 40}
```

`data/films.json` (сцены хранятся внутри фильма):

```json
{"id": 1, "title": "Полночный экспресс", "director": "А. Сергеев",
 "scenes": [{"number": 1, "description": "Прибытие поезда", "crew_size": 35}]}
```

`data/shootings.json` (связи — через идентификаторы):

```json
{"id": 1, "film_id": 1, "scene_number": 1, "location_id": 1,
 "shooting_date": "2026-10-20", "is_cancelled": false}
```

## Установка

```text
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python -m db.import_json      # создать data/kinoplan.sqlite из JSON
```

Пересоздать базу с нуля: удалить `data/kinoplan.sqlite` и снова выполнить `python -m db.import_json`. Проверить запросы вручную:

```text
sqlite3 -header -column data/kinoplan.sqlite
sqlite> .read sql/queries.sql
```

## Запуск

Веб-версия:

```text
python manage.py runserver
```

После запуска открыть http://127.0.0.1:8000/.

Консольная версия:

```text
python main.py
```

## Тестирование и качество кода

```text
pytest -v
flake8 . --extend-exclude=venv
python manage.py check
```

## План развития

- переход от ручных SQL-запросов к моделям Django ORM и миграциям;
- единое хранилище для консольной и веб-версии (сейчас консоль работает с JSON);
- формы создания фильмов, локаций и съёмок, отмена съёмки из веб-интерфейса;
- пользователи и разграничение доступа;
- разработка API, контейнеризация, CI/CD.

## История изменений по практическим работам

### ПР1. Основы Python: актуализация знаний и настройка рабочего окружения

Что сделано:

- выбрана тема проекта, создан Git-репозиторий и удалённый репозиторий на GitHub;
- настроено виртуальное окружение `venv` и конфигурация отладки VS Code;
- создан `.gitignore` и заполнен `README.md` (назначение, аудитория, предметная область, сущности, функции, план развития);
- в `main.py` реализован начальный сценарий: данные одной сцены хранятся в переменных простых типов, дата задаётся через модуль `datetime`;
- реализованы функции `check_location_availability()`, `get_days_until_shooting()`, `get_shooting_status()`.

Отладка: в `main.py` была намеренно внесена ошибка — в функции `get_days_until_shooting` порядок вычитания дат был перепутан (`today - shoot_date` вместо `shoot_date - today`), из-за чего дата съёмки в будущем ошибочно определялась как уже прошедшая.

1. Установлен breakpoint на строке вычисления `delta` в функции `get_days_until_shooting`.
2. Программа запущена в режиме отладки IDE.
3. Выполнение пройдено пошагово до точки останова.
4. Проверены значения переменных `today`, `shoot_date` и `delta.days` — обнаружено, что `delta.days` отрицательное, хотя дата съёмки позже текущей.
5. Причина ошибки установлена: перепутан порядок операндов при вычитании дат.
6. Ошибка исправлена на `delta = shoot_date - today`, работа программы проверена повторным запуском.

### ПР2. Коллекции, функции, циклы и расширенные возможности Python

Что изменилось по сравнению с ПР1:

- **данные → коллекции:** одиночные переменные заменены коллекциями — локации и фильмы хранятся словарями `{id: запись}`, сцены — списком внутри фильма, съёмки — списком словарей;
- **разбиение на модули:** код разделён на `locations.py`, `films.py`, `shootings.py`, `storage.py`, `utils.py`; `main.py` стал точкой запуска с меню из 12 пунктов и конструкцией `if __name__ == "__main__"`;
- **новые функции:** добавление, поиск, отбор и сортировка локаций; добавление фильмов и сцен; проверка вместимости и доступности локации; назначение и отмена съёмок; график съёмок;
- **функции ПР1 сохранены:** перенесены в `shootings.py` и используются вместе с новыми (например, статус занятости выводится по результату `is_location_available()`); `get_days_until_shooting()` получила необязательный параметр `today`;
- **файлы JSON:** данные хранятся в `data/*.json`, читаются и записываются через контекстный менеджер `with` и сохраняются после каждого изменения;
- **исключения:** обрабатываются некорректный ввод чисел и дат (`ValueError`), несуществующие фильм/сцена/локация (`KeyError`), отсутствующий или повреждённый файл (`FileNotFoundError`, `JSONDecodeError`), прерывание ввода (`KeyboardInterrupt`, `EOFError`);
- **расширенные возможности:** генератор `filter_locations_by_capacity()`, lambda-функции в сортировках, интроспекция (`inspect`, `__doc__`) в пункте меню «Справка по функциям»;
- **качество кода:** docstring и аннотации типов у основных функций, проверка `flake8` без замечаний, `requirements.txt`, `pytest.ini`, `.flake8`;
- **тестирование:** каталог `tests/` с 16 тестами pytest для локаций, фильмов, съёмок и хранилища.

### ПР3. Объектно-ориентированное программирование

Что изменилось по сравнению с ПР2:

- **словари → объекты:** сущности стали классами `Location`, `Film`, `Scene`, `Shooting` в пакете `models/`; коллекции `dict[int, dict]` и `list[dict]` заменены на `List[Location]`, `List[Film]`, `List[Shooting]`;
- **модули переехали в пакет:** `locations.py`, `films.py`, `shootings.py` перенесены в `models/`, классы импортируются через `models/__init__.py`;
- **операции стали методами:** проверка вместимости — `Location.is_suitable_for()` (функция `check_location_capacity()` теперь вызывает его), добавление сцены — `Film.add_scene()`, отмена — `Shooting.cancel()`; функции работы с коллекциями (поиск, отбор, сортировка) остались обычными функциями;
- **взаимодействие объектов:** `Shooting` хранит ссылки на объекты `Film`, `Scene`, `Location`, а не их id;
- **отмена без удаления:** `cancel_shooting()` больше не удаляет съёмку — она помечается отменённой, остаётся в истории и не блокирует локацию; в JSON добавлено поле `is_cancelled`;
- **принципы ООП:** наследование от базового класса `Entity`, полиморфный `to_data()`, инкапсуляция признака отмены (`_is_cancelled` + свойство `is_cancelled`), `__str__()` у всех классов;
- **декораторы методов:** `@staticmethod Location.validate_capacity()`, `@classmethod from_data()`, `@property` для `is_cancelled` и `status`;
- **хранение:** `storage.py` преобразует JSON в объекты и обратно, при загрузке съёмок восстанавливает связи по id; добавлены функции поиска `find_*_by_id()`;
- **тесты:** тесты ПР2 адаптированы к объектам, добавлены тесты классов, связей объектов, отмены и восстановления связей из JSON (26 тестов).

### ПР5. Django, HTTP и основы веб-разработки

Что изменилось по сравнению с ПР3:

- **Django-проект:** в корне репозитория создан проект `kinoplan` (`manage.py`, `settings.py` с русской локалью и часовым поясом Москвы);
- **Django-приложения:** `homepage`, `films`, `locations`, `shootings`, зарегистрированы в `INSTALLED_APPS`;
- **маршрутизация двух уровней:** корневой `kinoplan/urls.py` подключает `urls.py` приложений через `include()`; динамические адреса используют конвертер `<int:...>`, у маршрутов заданы имена `name=`;
- **view-функции:** 7 страниц, формирующих HTML-ответ; несуществующий объект — ответ с кодом 404, неизвестный адрес — собственная страница `handler404`;
- **HTML/CSS/Bootstrap:** общий каркас `page()` с Bootstrap 5.3 (CDN), навигационная панель, таблицы, карточки, бейджи статусов, форма выбора даты (GET-запрос);
- **связь с ПР3:** страницы получают данные через `storage.py` и классы `models/`, используют `find_*_by_id()`, `is_location_available()`, `sort_locations()`, свойство `Shooting.status`; логика не дублируется;
- **консольная версия сохранена:** `main.py`, JSON-хранилище и все тесты ПР3 работают без изменений;
- **окружение:** Python 3.11, в `requirements.txt` добавлен `Django==5.2.*`, `db.sqlite3` добавлен в `.gitignore`; сгенерированные заготовки очищены от неиспользуемых импортов для flake8;
- **тесты:** добавлен `tests/test_views.py` (тестовый клиент Django): коды ответов страниц, отображение данных, проверка даты, 404 (всего 41 тест).

### ПР6. Шаблоны Django и проектная разработка

Что изменилось по сравнению с ПР5:

- **HTML вынесен из Python в шаблоны:** все view-функции вызывают `render(request, шаблон, context)`; функции `page()` и `not_found_page()` удалены из `homepage/views.py`;
- **базовый шаблон:** `templates/base.html` с блоками `title` и `content`, каталог `templates/` подключён в `TEMPLATES["DIRS"]`; все страницы наследуют его через `{% extends %}`;
- **включаемые шаблоны:** навигация, карточка фильма, строка локации, бейдж статуса и строка съёмки вынесены в `includes/` и подключаются через `{% include %}` (статус съёмки используется на пяти страницах);
- **контекст, циклы, условия:** данные передаются через `context`, списки выводятся `{% for %}` с `{% empty %}`, статусы и «объект не найден» — через `{% if %}`; при отсутствии объекта ответ по-прежнему имеет код 404;
- **именованные URL:** у приложений появились `app_name`, маршруты переименованы в `list`/`detail`, все ссылки строятся тегом `{% url %}`;
- **фильтры:** `length`, `default`, `date:"d.m.Y"`, `slice`;
- **статические файлы:** собственные `style.css`, `main.js` (год в подвале, скрытие отменённых съёмок) и `logo.png`; Bootstrap оставлен для базовой вёрстки;
- **данные:** в JSON добавлены второй фильм, четвёртая локация и будущие съёмки, чтобы на страницах были видны все статусы;
- **тесты:** в `tests/test_views.py` добавлены проверки используемых шаблонов и include, именованных URL, статических файлов, фильтров, пустых коллекций и удаления `page()` (всего 58 тестов).

### ПР7. Основы баз данных и SQL

Что изменилось по сравнению с ПР6:

- **база данных:** `data/kinoplan.sqlite`, таблицы `films`, `scenes`, `locations`, `shootings` в `sql/schema.sql`; первичные и внешние ключи, `NOT NULL`, `DEFAULT`, `CHECK`, `UNIQUE`; сцены вынесены из фильма в отдельную таблицу;
- **правило двойного бронирования в базе:** частичный уникальный индекс не даёт назначить две активные съёмки на одну локацию в один день;
- **работа из Python:** `db/database.py` (подключение, `PRAGMA foreign_keys = ON`, `sqlite3.Row`), `db/import_json.py` (перенос JSON → SQLite через `executemany`, транзакция с `commit`/`rollback`, повторный запуск безопасен);
- **SQL-запросы:** 25 запросов в `sql/queries.sql`, проверены в SQLite CLI; выборка, WHERE (`=`, `>=`, `BETWEEN`, `LIKE`, `IS NULL`), JOIN и LEFT JOIN, подзапрос `NOT IN`, `COUNT/MIN/MAX/AVG/SUM`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT/OFFSET`, `DISTINCT`;
- **веб-интерфейс на SQLite:** все страницы получают данные запросами из `db/queries.py` (19 функций), значения передаются параметрами `?`; новые страницы — поиск свободных локаций на дату (`/locations/free/`) и статистика (`/shootings/statistics/`), подбор локаций по размеру группы, пункт «Статистика» в навигации;
- **предметная логика:** текст статуса вынесен в `get_status_text()` и используется и объектом `Shooting`, и строками из базы; функция ПР1 `check_location_availability()` по-прежнему формирует сообщение о занятости;
- **данные:** добавлена сцена без съёмки, чтобы запрос `LEFT JOIN … IS NULL` возвращал непустой результат;
- **тесты:** `conftest.py` собирает временную базу из JSON и подменяет `DB_PATH`; `tests/test_database.py` проверяет схему, внешние ключи и ограничения, импорт, запросы WHERE/JOIN/GROUP BY/HAVING и новые страницы (всего 81 тест).
