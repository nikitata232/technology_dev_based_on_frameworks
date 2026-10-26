"""SQL-запросы веб-интерфейса КиноПлан.

Каждая функция выполняет один запрос к SQLite и возвращает строки
sqlite3.Row (доступ к полям по именам) или словари. Значения от
пользователя передаются только параметрами ?, текст запроса не меняется.
Эти же запросы с примерами значений сохранены в sql/queries.sql.
"""
from datetime import date
from typing import List, Optional

from db.database import fetch_all, fetch_one
from models.shootings import get_days_until_shooting, get_status_text


def prepare_shootings(rows) -> List[dict]:
    """Дополнить строки съёмок датой, числом дней и текстом статуса.

    SQLite хранит дату строкой ГГГГ-ММ-ДД; она превращается в date,
    чтобы в шаблоне работал фильтр date. Статус считают функции ПР1.
    """
    shootings = []
    for row in rows:
        shooting = dict(row)
        shooting_date = date.fromisoformat(row["shooting_date"])
        days_until = get_days_until_shooting(shooting_date)
        shooting["shooting_date"] = shooting_date
        shooting["is_cancelled"] = bool(row["is_cancelled"])
        shooting["days_until"] = days_until
        shooting["status"] = get_status_text(
            shooting["is_cancelled"], days_until
        )
        shootings.append(shooting)
    return shootings


# ---------- Главная страница ----------

def get_summary():
    """Агрегат: число фильмов, локаций и активных съёмок."""
    return fetch_one("""
        SELECT
            (SELECT COUNT(*) FROM films) AS films_count,
            (SELECT COUNT(*) FROM locations) AS locations_count,
            (SELECT COUNT(*) FROM shootings
             WHERE is_cancelled = 0) AS active_count
    """)


def get_upcoming_shootings(today: date, limit: int = 3) -> List[dict]:
    """JOIN + WHERE + LIMIT: ближайшие активные съёмки начиная с today."""
    rows = fetch_all("""
        SELECT
            shootings.id,
            shootings.shooting_date,
            shootings.is_cancelled,
            films.title AS film_title,
            scenes.number AS scene_number,
            locations.name AS location_name
        FROM shootings
        JOIN scenes ON shootings.scene_id = scenes.id
        JOIN films ON scenes.film_id = films.id
        JOIN locations ON shootings.location_id = locations.id
        WHERE shootings.is_cancelled = 0
          AND shootings.shooting_date >= ?
        ORDER BY shootings.shooting_date, shootings.id
        LIMIT ?
    """, [today.isoformat(), limit])
    return prepare_shootings(rows)


# ---------- Фильмы ----------

def get_films():
    """LEFT JOIN + GROUP BY: фильмы с количеством сцен."""
    return fetch_all("""
        SELECT
            films.id,
            films.title,
            films.director,
            COUNT(scenes.id) AS scenes_count
        FROM films
        LEFT JOIN scenes ON scenes.film_id = films.id
        GROUP BY films.id, films.title, films.director
        ORDER BY films.title
    """)


def get_film(film_id: int):
    """WHERE: фильм по идентификатору (None, если его нет)."""
    return fetch_one("""
        SELECT id, title, director
        FROM films
        WHERE id = ?
    """, [film_id])


def get_scenes(film_id: int):
    """WHERE + ORDER BY: сцены фильма по порядку."""
    return fetch_all("""
        SELECT number, description, crew_size
        FROM scenes
        WHERE film_id = ?
        ORDER BY number
    """, [film_id])


def get_film_shootings(film_id: int) -> List[dict]:
    """JOIN + WHERE: съёмки одного фильма."""
    rows = fetch_all("""
        SELECT
            shootings.id,
            shootings.shooting_date,
            shootings.is_cancelled,
            films.title AS film_title,
            scenes.number AS scene_number,
            locations.name AS location_name
        FROM shootings
        JOIN scenes ON shootings.scene_id = scenes.id
        JOIN films ON scenes.film_id = films.id
        JOIN locations ON shootings.location_id = locations.id
        WHERE films.id = ?
        ORDER BY shootings.shooting_date
    """, [film_id])
    return prepare_shootings(rows)


# ---------- Локации ----------

def get_locations(min_capacity: int = 0):
    """WHERE + ORDER BY: локации вместимостью от min_capacity человек."""
    return fetch_all("""
        SELECT id, name, address, capacity
        FROM locations
        WHERE capacity >= ?
        ORDER BY capacity DESC, name
    """, [min_capacity])


def get_location(location_id: int):
    """WHERE: локация по идентификатору (None, если её нет)."""
    return fetch_one("""
        SELECT id, name, address, capacity
        FROM locations
        WHERE id = ?
    """, [location_id])


def is_location_busy(location_id: int, check_date: date) -> bool:
    """COUNT + WHERE: есть ли на локации активная съёмка в эту дату."""
    row = fetch_one("""
        SELECT COUNT(*) AS busy_count
        FROM shootings
        WHERE location_id = ?
          AND shooting_date = ?
          AND is_cancelled = 0
    """, [location_id, check_date.isoformat()])
    return row["busy_count"] > 0


def get_location_shootings(location_id: int) -> List[dict]:
    """JOIN + WHERE: съёмки на одной локации."""
    rows = fetch_all("""
        SELECT
            shootings.id,
            shootings.shooting_date,
            shootings.is_cancelled,
            films.title AS film_title,
            scenes.number AS scene_number,
            locations.name AS location_name
        FROM shootings
        JOIN scenes ON shootings.scene_id = scenes.id
        JOIN films ON scenes.film_id = films.id
        JOIN locations ON shootings.location_id = locations.id
        WHERE locations.id = ?
        ORDER BY shootings.shooting_date
    """, [location_id])
    return prepare_shootings(rows)


def find_free_locations(check_date: date, crew_size: int):
    """Подзапрос NOT IN: локации, свободные в дату и вмещающие группу."""
    return fetch_all("""
        SELECT id, name, address, capacity
        FROM locations
        WHERE capacity >= ?
          AND id NOT IN (
              SELECT location_id
              FROM shootings
              WHERE shooting_date = ?
                AND is_cancelled = 0
          )
        ORDER BY capacity, name
    """, [crew_size, check_date.isoformat()])


# ---------- Съёмки ----------

def get_shootings() -> List[dict]:
    """JOIN четырёх таблиц: полный график съёмок по датам."""
    rows = fetch_all("""
        SELECT
            shootings.id,
            shootings.shooting_date,
            shootings.is_cancelled,
            films.title AS film_title,
            scenes.number AS scene_number,
            locations.name AS location_name
        FROM shootings
        JOIN scenes ON shootings.scene_id = scenes.id
        JOIN films ON scenes.film_id = films.id
        JOIN locations ON shootings.location_id = locations.id
        ORDER BY shootings.shooting_date, shootings.id
    """)
    return prepare_shootings(rows)


def get_shooting(shooting_id: int) -> Optional[dict]:
    """JOIN + WHERE: одна съёмка со сведениями о фильме, сцене, локации."""
    rows = fetch_all("""
        SELECT
            shootings.id,
            shootings.shooting_date,
            shootings.is_cancelled,
            films.id AS film_id,
            films.title AS film_title,
            films.director AS film_director,
            scenes.number AS scene_number,
            scenes.description AS scene_description,
            scenes.crew_size,
            locations.id AS location_id,
            locations.name AS location_name,
            locations.address AS location_address,
            locations.capacity AS location_capacity
        FROM shootings
        JOIN scenes ON shootings.scene_id = scenes.id
        JOIN films ON scenes.film_id = films.id
        JOIN locations ON shootings.location_id = locations.id
        WHERE shootings.id = ?
    """, [shooting_id])
    shootings = prepare_shootings(rows)
    return shootings[0] if shootings else None


# ---------- Статистика ----------

def get_shooting_totals():
    """Агрегаты по всем съёмкам: количество, отменённые, период."""
    return fetch_one("""
        SELECT
            COUNT(*) AS total,
            COUNT(CASE WHEN is_cancelled = 0 THEN 1 END) AS active,
            COUNT(CASE WHEN is_cancelled = 1 THEN 1 END) AS cancelled,
            strftime('%d.%m.%Y', MIN(shooting_date)) AS first_date,
            strftime('%d.%m.%Y', MAX(shooting_date)) AS last_date
        FROM shootings
    """)


def get_location_statistics():
    """LEFT JOIN + GROUP BY: активные съёмки по каждой локации.

    LEFT JOIN оставляет в результате локации без съёмок (счётчик 0).
    """
    return fetch_all("""
        SELECT
            locations.id,
            locations.name,
            locations.capacity,
            COUNT(shootings.id) AS shootings_count,
            strftime('%d.%m.%Y', MIN(shootings.shooting_date)) AS first_date,
            strftime('%d.%m.%Y', MAX(shootings.shooting_date))
                AS last_date
        FROM locations
        LEFT JOIN shootings
            ON shootings.location_id = locations.id
           AND shootings.is_cancelled = 0
        GROUP BY locations.id, locations.name, locations.capacity
        ORDER BY shootings_count DESC, locations.name
    """)


def get_film_statistics():
    """LEFT JOIN + GROUP BY + AVG/MAX: сцены и группы по фильмам."""
    return fetch_all("""
        SELECT
            films.id,
            films.title,
            COUNT(scenes.id) AS scenes_count,
            ROUND(AVG(scenes.crew_size), 1) AS avg_crew,
            MAX(scenes.crew_size) AS max_crew,
            SUM(scenes.crew_size) AS total_crew
        FROM films
        LEFT JOIN scenes ON scenes.film_id = films.id
        GROUP BY films.id, films.title
        ORDER BY films.title
    """)


def get_busy_locations(min_count: int):
    """GROUP BY + HAVING: локации, где активных съёмок не меньше min_count."""
    return fetch_all("""
        SELECT
            locations.id,
            locations.name,
            COUNT(*) AS shootings_count
        FROM shootings
        JOIN locations ON shootings.location_id = locations.id
        WHERE shootings.is_cancelled = 0
        GROUP BY locations.id, locations.name
        HAVING COUNT(*) >= ?
        ORDER BY shootings_count DESC
    """, [min_count])


def get_shootings_by_month():
    """GROUP BY по месяцу: сколько активных съёмок в каждом месяце."""
    return fetch_all("""
        SELECT
            strftime('%m.%Y', shooting_date) AS month,
            COUNT(*) AS shootings_count
        FROM shootings
        WHERE is_cancelled = 0
        GROUP BY strftime('%Y-%m', shooting_date)
        ORDER BY strftime('%Y-%m', shooting_date)
    """)


def get_unscheduled_scenes():
    """LEFT JOIN + IS NULL: сцены, для которых нет активной съёмки."""
    return fetch_all("""
        SELECT
            films.id AS film_id,
            films.title AS film_title,
            scenes.number AS scene_number,
            scenes.description,
            scenes.crew_size
        FROM scenes
        JOIN films ON scenes.film_id = films.id
        LEFT JOIN shootings
            ON shootings.scene_id = scenes.id
           AND shootings.is_cancelled = 0
        WHERE shootings.id IS NULL
        ORDER BY films.title, scenes.number
    """)
