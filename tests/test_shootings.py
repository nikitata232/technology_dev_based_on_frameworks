from datetime import date

from models import Film, Location, Shooting
from models.shootings import (
    cancel_shooting,
    create_shooting,
    get_days_until_shooting,
    get_shooting_status,
    is_location_available,
)

SHOOT_DATE = date(2026, 10, 20)


def make_objects():
    film = Film(1, "Полночный экспресс", "А. Сергеев")
    film.add_scene("Прибытие поезда", 35)
    film.add_scene("Разговор в купе", 10)
    location = Location(1, "Вокзал, павильон 3", "ул. Каланчёвская", 40)
    return film, location


def test_shooting_creation_links_objects():
    film, location = make_objects()
    scene = film.get_scene(1)
    shooting = Shooting(1, film, scene, location, SHOOT_DATE)
    assert shooting.film is film
    assert shooting.scene is scene
    assert shooting.location is location
    assert shooting.location.name == "Вокзал, павильон 3"
    assert not shooting.is_cancelled


def test_shooting_cancel():
    film, location = make_objects()
    shooting = Shooting(1, film, film.get_scene(1), location, SHOOT_DATE)
    shooting.cancel()
    assert shooting.is_cancelled
    assert shooting.status == "Съёмка отменена"


def test_shooting_to_data_uses_ids():
    film, location = make_objects()
    shooting = Shooting(7, film, film.get_scene(2), location, SHOOT_DATE)
    assert shooting.to_data() == {
        "id": 7,
        "film_id": 1,
        "scene_number": 2,
        "location_id": 1,
        "shooting_date": "2026-10-20",
        "is_cancelled": False,
    }


def test_location_available_when_no_shootings():
    _, location = make_objects()
    assert is_location_available([], location, SHOOT_DATE)


def test_duplicate_shooting_forbidden():
    film, location = make_objects()
    shootings = []
    first = create_shooting(
        shootings, film, film.get_scene(1), location, SHOOT_DATE
    )
    assert isinstance(first, Shooting)
    second = create_shooting(
        shootings, film, film.get_scene(2), location, SHOOT_DATE
    )
    assert second is None
    assert len(shootings) == 1


def test_cancelled_shooting_frees_location():
    film, location = make_objects()
    shootings = []
    first = create_shooting(
        shootings, film, film.get_scene(1), location, SHOOT_DATE
    )
    assert cancel_shooting(shootings, first.id)
    assert first in shootings
    assert is_location_available(shootings, location, SHOOT_DATE)
    again = create_shooting(
        shootings, film, film.get_scene(2), location, SHOOT_DATE
    )
    assert again is not None
    assert not cancel_shooting(shootings, first.id)
    assert not cancel_shooting(shootings, 99)


def test_days_and_status():
    days = get_days_until_shooting(SHOOT_DATE, today=date(2026, 10, 5))
    assert days == 15
    assert get_shooting_status(days) == "До съёмки осталось 15 дн."
    assert get_shooting_status(0) == "Съёмка сегодня"
    assert get_shooting_status(-1) == "Съёмка уже прошла"
