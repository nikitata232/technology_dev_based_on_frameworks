"""Тесты слоя базы данных (ПР7): схема, импорт, SQL-запросы, страницы."""
import shutil
import sqlite3
from contextlib import closing
from datetime import date

import pytest
from django.test import Client

from db import database, queries
from storage import load_films, load_locations, load_shootings


@pytest.fixture
def client():
    return Client()


def scalar(sql, params=()):
    with closing(database.get_connection()) as conn:
        return conn.execute(sql, params).fetchone()[0]


# --- схема и импорт ---

def test_tables_created():
    names = {row["name"] for row in database.fetch_all(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"films", "scenes", "locations", "shootings"} <= names


def test_foreign_keys_declared():
    with closing(database.get_connection()) as conn:
        targets = {row["table"] for row in conn.execute(
            "PRAGMA foreign_key_list(shootings)")}
    assert targets == {"scenes", "locations"}


def test_import_counts_match_json():
    films = load_films()
    locations = load_locations()
    shootings = load_shootings(films, locations)
    assert scalar("SELECT COUNT(*) FROM films") == len(films)
    assert scalar("SELECT COUNT(*) FROM scenes") == sum(
        len(film.scenes) for film in films)
    assert scalar("SELECT COUNT(*) FROM locations") == len(locations)
    assert scalar("SELECT COUNT(*) FROM shootings") == len(shootings)


def test_foreign_key_violation_rejected():
    with closing(database.get_connection()) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO shootings (scene_id, location_id, shooting_date)"
                " VALUES (1, 999, '2026-12-01')")


def test_double_booking_rejected():
    with closing(database.get_connection()) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO shootings (scene_id, location_id, shooting_date)"
                " VALUES (1, 1, '2026-11-10')")
        conn.execute(
            "INSERT INTO shootings"
            " (scene_id, location_id, shooting_date, is_cancelled)"
            " VALUES (1, 1, '2026-11-10', 1)")
        conn.rollback()


# --- запросы ---

def test_rows_accessible_by_name():
    film = queries.get_film(1)
    assert film["title"] == "Полночный экспресс"


def test_get_locations_where_capacity():
    names = [row["name"] for row in queries.get_locations(50)]
    assert names == ["Студия «Север»", "Набережная парка"]


def test_location_busy_ignores_cancelled():
    assert queries.is_location_busy(1, date(2026, 10, 20))
    assert not queries.is_location_busy(3, date(2026, 10, 22))


def test_free_locations():
    free = queries.find_free_locations(date(2026, 11, 10), 1)
    assert [row["id"] for row in free] == [3, 4]
    free = queries.find_free_locations(date(2026, 11, 10), 40)
    assert [row["name"] for row in free] == ["Набережная парка"]


def test_shootings_join_and_status():
    shooting = queries.get_shooting(2)
    assert shooting["film_title"] == "Полночный экспресс"
    assert shooting["location_name"] == "Квартира на Арбате"
    assert shooting["status"] == "Съёмка отменена"


def test_films_group_by_scene_count():
    counts = {row["title"]: row["scenes_count"] for row in queries.get_films()}
    assert counts == {"Полночный экспресс": 3, "Северное сияние": 4}


def test_location_statistics_left_join_keeps_zero():
    stats = {row["name"]: row["shootings_count"]
             for row in queries.get_location_statistics()}
    assert stats["Вокзал, павильон 3"] == 3
    assert stats["Набережная парка"] == 0


def test_busy_locations_having():
    names = [row["name"] for row in queries.get_busy_locations(2)]
    assert names == ["Вокзал, павильон 3", "Квартира на Арбате"]
    assert len(queries.get_busy_locations(3)) == 1
    assert queries.get_busy_locations(10) == []


def test_unscheduled_scenes_is_null():
    rows = queries.get_unscheduled_scenes()
    assert [row["description"] for row in rows] == [
        "Эпилог: рассвет над рекой"]


def test_totals_aggregates():
    totals = queries.get_shooting_totals()
    assert (totals["total"], totals["active"], totals["cancelled"]) == (
        7, 6, 1)
    assert totals["first_date"] == "20.10.2026"


def test_missing_database_message(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "none.sqlite"))
    with pytest.raises(FileNotFoundError, match="db.import_json"):
        queries.get_films()


# --- страницы ---

def test_page_shows_data_from_database(client, monkeypatch, tmp_path,
                                       test_db_path):
    copy = str(tmp_path / "copy.sqlite")
    shutil.copy(test_db_path, copy)
    with closing(database.get_connection(copy)) as conn:
        conn.execute("UPDATE locations SET name = 'Изменено в SQLite'"
                     " WHERE id = 1")
        conn.commit()
    monkeypatch.setattr(database, "DB_PATH", copy)
    assert "Изменено в SQLite" in client.get("/locations/").content.decode()


def test_locations_capacity_filter_page(client):
    html = client.get("/locations/?capacity=50").content.decode()
    assert "Студия «Север»" in html
    assert "Квартира на Арбате" not in html


def test_free_locations_page(client):
    response = client.get("/locations/free/?date=2026-11-10&crew=40")
    html = response.content.decode()
    assert response.status_code == 200
    assert "Набережная парка" in html
    assert "Студия «Север»" not in html


def test_free_locations_bad_date(client):
    html = client.get("/locations/free/?date=abc").content.decode()
    assert "Некорректная дата" in html


def test_statistics_page(client):
    response = client.get("/shootings/statistics/?min=3")
    html = response.content.decode()
    assert response.status_code == 200
    assert "Статистика съёмок" in html
    assert "Эпилог: рассвет над рекой" in html


def test_statistics_bad_min_falls_back(client):
    assert client.get("/shootings/statistics/?min=x").status_code == 200


def test_navigation_has_statistics(client):
    html = client.get("/").content.decode()
    assert 'href="/shootings/statistics/"' in html
