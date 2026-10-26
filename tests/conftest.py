"""Настройка Django и тестовой базы SQLite для тестов."""
import os

import django
import pytest
from django.test.utils import setup_test_environment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kinoplan.settings")
django.setup()
setup_test_environment()

from db import database  # noqa: E402
from db.import_json import import_all  # noqa: E402
from storage import load_films, load_locations, load_shootings  # noqa: E402


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Собрать временную базу из data/*.json один раз на все тесты."""
    path = str(tmp_path_factory.mktemp("db") / "kinoplan_test.sqlite")
    films = load_films()
    locations = load_locations()
    conn = database.get_connection(path)
    try:
        import_all(conn, films, locations, load_shootings(films, locations))
    finally:
        conn.close()
    return path


@pytest.fixture(autouse=True)
def use_test_db(monkeypatch, test_db_path):
    """Направить все запросы к SQLite во временную базу."""
    monkeypatch.setattr(database, "DB_PATH", test_db_path)
