"""Перенос данных проекта из JSON-файлов в базу SQLite.

Запуск из корня проекта:
    python -m db.import_json

JSON читается функциями storage.py (ПР3), поэтому записи проходят ту же
проверку, что и в консольной версии. Скрипт можно запускать повторно:
таблицы создаются с IF NOT EXISTS, старые записи перед импортом удаляются.
"""
import sqlite3
from typing import List

from db.database import DB_PATH, create_schema, get_connection
from models import Film, Location, Shooting
from storage import load_films, load_locations, load_shootings


def clear_tables(conn: sqlite3.Connection) -> None:
    """Удалить старые записи: сначала зависимые таблицы, затем главные."""
    conn.execute("DELETE FROM shootings")
    conn.execute("DELETE FROM scenes")
    conn.execute("DELETE FROM locations")
    conn.execute("DELETE FROM films")


def import_films(conn: sqlite3.Connection, films: List[Film]) -> None:
    """Перенести фильмы и их сцены (сцены — в отдельную таблицу)."""
    conn.executemany(
        """
        INSERT INTO films (id, title, director)
        VALUES (?, ?, ?)
        """,
        [(film.id, film.title, film.director or None) for film in films],
    )
    conn.executemany(
        """
        INSERT INTO scenes (film_id, number, description, crew_size)
        VALUES (?, ?, ?, ?)
        """,
        [
            (film.id, scene.number, scene.description, scene.crew_size)
            for film in films
            for scene in film.scenes
        ],
    )


def import_locations(
    conn: sqlite3.Connection,
    locations: List[Location],
) -> None:
    """Перенести локации."""
    conn.executemany(
        """
        INSERT INTO locations (id, name, address, capacity)
        VALUES (?, ?, ?, ?)
        """,
        [
            (loc.id, loc.name, loc.address or None, loc.capacity)
            for loc in locations
        ],
    )


def import_shootings(
    conn: sqlite3.Connection,
    shootings: List[Shooting],
) -> None:
    """Перенести съёмки.

    В JSON съёмка ссылается на фильм и номер сцены, а в базе — на
    scenes.id. Нужный id находит подзапрос по паре (film_id, number).
    """
    conn.executemany(
        """
        INSERT INTO shootings (
            id, scene_id, location_id, shooting_date, is_cancelled
        )
        VALUES (
            ?,
            (SELECT id FROM scenes WHERE film_id = ? AND number = ?),
            ?, ?, ?
        )
        """,
        [
            (
                shooting.id,
                shooting.film.id,
                shooting.scene.number,
                shooting.location.id,
                shooting.shooting_date.isoformat(),
                int(shooting.is_cancelled),
            )
            for shooting in shootings
        ],
    )


def import_all(
    conn: sqlite3.Connection,
    films: List[Film],
    locations: List[Location],
    shootings: List[Shooting],
) -> None:
    """Создать схему и перенести все данные одной транзакцией.

    Порядок важен из-за внешних ключей: фильмы и сцены, локации,
    и только потом съёмки, которые на них ссылаются.
    """
    create_schema(conn)
    try:
        clear_tables(conn)
        import_films(conn, films)
        import_locations(conn, locations)
        import_shootings(conn, shootings)
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def main() -> None:
    """Загрузить JSON-файлы data/ и перенести их в data/kinoplan.sqlite."""
    films = load_films()
    locations = load_locations()
    shootings = load_shootings(films, locations)
    conn = get_connection()
    try:
        import_all(conn, films, locations, shootings)
    finally:
        conn.close()
    print(f"База {DB_PATH}: фильмов {len(films)}, "
          f"сцен {sum(len(f.scenes) for f in films)}, "
          f"локаций {len(locations)}, съёмок {len(shootings)}.")


if __name__ == "__main__":
    main()
