"""Подключение к базе данных SQLite проекта КиноПлан."""
import os
import sqlite3
from contextlib import closing
from typing import List, Optional, Sequence

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "kinoplan.sqlite")
SCHEMA_FILE = os.path.join(BASE_DIR, "sql", "schema.sql")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Открыть соединение с базой и настроить его.

    row_factory = sqlite3.Row — к полям строки результата можно
    обращаться по именам: row["title"] в Python, {{ row.title }}
    в шаблоне. PRAGMA foreign_keys = ON включает проверку внешних
    ключей (по умолчанию SQLite её не выполняет).
    """
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Создать таблицы по sql/schema.sql (повторный запуск безопасен)."""
    with open(SCHEMA_FILE, encoding="utf-8") as file:
        conn.executescript(file.read())


def check_database() -> None:
    """Убедиться, что файл базы существует, иначе подсказать команду."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"База данных {DB_PATH} не найдена. "
            "Создайте её командой: python -m db.import_json"
        )


def fetch_all(query: str, params: Sequence = ()) -> List[sqlite3.Row]:
    """Выполнить SELECT и вернуть все строки результата.

    Значения передаются отдельно от текста запроса (параметры ?).
    """
    check_database()
    with closing(get_connection()) as conn:
        return conn.execute(query, params).fetchall()


def fetch_one(query: str, params: Sequence = ()) -> Optional[sqlite3.Row]:
    """Выполнить SELECT и вернуть первую строку или None."""
    check_database()
    with closing(get_connection()) as conn:
        return conn.execute(query, params).fetchone()
