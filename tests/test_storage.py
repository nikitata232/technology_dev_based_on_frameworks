from datetime import date

from models import Film, Location, Shooting
from storage import (
    load_films,
    load_json,
    load_locations,
    load_shootings,
    save_films,
    save_locations,
    save_shootings,
)


def test_save_and_load_locations(tmp_path):
    filename = str(tmp_path / "locations.json")
    save_locations([Location(1, "Студия", "пр. Мира", 5)], filename)
    loaded = load_locations(filename)
    assert isinstance(loaded[0], Location)
    assert loaded[0].name == "Студия"


def test_shootings_restore_links(tmp_path):
    film = Film(1, "Фильм", "Режиссёр")
    film.add_scene("Сцена", 5)
    location = Location(2, "Студия", "пр. Мира", 10)
    shooting = Shooting(1, film, film.get_scene(1), location,
                        date(2026, 10, 20), is_cancelled=True)
    films_file = str(tmp_path / "films.json")
    shootings_file = str(tmp_path / "shootings.json")
    save_films([film], films_file)
    save_shootings([shooting], shootings_file)

    films = load_films(films_file)
    loaded = load_shootings(films, [location], shootings_file)
    assert loaded[0].film is films[0]
    assert loaded[0].location is location
    assert loaded[0].is_cancelled
    assert loaded[0].shooting_date == date(2026, 10, 20)


def test_shooting_with_unknown_location_skipped(tmp_path):
    film = Film(1, "Фильм", "Режиссёр")
    film.add_scene("Сцена", 5)
    location = Location(2, "Студия", "пр. Мира", 10)
    filename = str(tmp_path / "shootings.json")
    save_shootings(
        [Shooting(1, film, film.get_scene(1), location, date(2026, 1, 1))],
        filename,
    )
    assert load_shootings([film], [], filename) == []


def test_load_missing_file(tmp_path):
    assert load_json(str(tmp_path / "missing.json")) == []


def test_load_broken_json(tmp_path):
    filename = tmp_path / "broken.json"
    filename.write_text("{не json", encoding="utf-8")
    assert load_json(str(filename)) == []
