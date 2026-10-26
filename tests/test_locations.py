import pytest

from models import Location
from models.locations import (
    add_location,
    check_location_capacity,
    filter_locations_by_capacity,
    find_location,
    find_location_by_id,
    sort_locations,
)


def make_locations():
    locations = []
    add_location(locations, "Вокзал, павильон 3", "ул. Каланчёвская", 40)
    add_location(locations, "Студия «Север»", "пр. Мира", 80)
    add_location(locations, "Квартира на Арбате", "ул. Арбат", 12)
    return locations


def test_location_creation():
    location = Location(1, "Студия", "пр. Мира", 80)
    assert location.id == 1
    assert location.name == "Студия"
    assert location.capacity == 80


def test_location_str():
    location = Location(1, "Студия", "пр. Мира", 80)
    assert str(location) == "Студия (пр. Мира), до 80 чел."


def test_location_is_suitable_for():
    location = Location(1, "Студия", "пр. Мира", 30)
    assert location.is_suitable_for(20)
    assert not location.is_suitable_for(40)


def test_validate_capacity():
    assert Location.validate_capacity(10)
    assert not Location.validate_capacity(0)
    with pytest.raises(ValueError):
        Location(1, "Студия", "пр. Мира", 0)


def test_add_location_returns_object():
    locations = []
    location = add_location(locations, "Студия", "пр. Мира", 80)
    assert isinstance(location, Location)
    assert locations == [location]
    assert location.id == 1


def test_find_location_ignores_case():
    found = find_location(make_locations(), "студия")
    assert [location.id for location in found] == [2]


def test_find_location_by_id():
    locations = make_locations()
    assert find_location_by_id(locations, 3).name == "Квартира на Арбате"
    assert find_location_by_id(locations, 99) is None


def test_check_location_capacity():
    locations = make_locations()
    assert check_location_capacity(locations, 1, 40)
    assert not check_location_capacity(locations, 3, 20)
    with pytest.raises(KeyError):
        check_location_capacity(locations, 99, 5)


def test_filter_and_sort_locations():
    suitable = filter_locations_by_capacity(make_locations(), 30)
    result = sort_locations(list(suitable), reverse=True)
    assert [location.id for location in result] == [2, 1]
