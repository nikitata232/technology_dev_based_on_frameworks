"""Настройка Django и тестовой базы SQLite для тестов."""
import pytest

from db import database
from db.import_json import import_all
from storage import load_films, load_locations, load_shootings


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


@pytest.fixture(autouse=True)
def orm_data(db, test_db_path):
    """Каждый тест получает независимую копию данных через ORM."""
    from django.core.management import call_command
    call_command("import_legacy", source=test_db_path, verbosity=0)
