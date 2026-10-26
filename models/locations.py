"""Класс Location и функции работы с коллекцией локаций."""
from typing import Iterator, List, Optional

from .base import Entity


class Location(Entity):
    """Локация (место съёмок)."""

    def __init__(
        self,
        location_id: int,
        name: str,
        address: str,
        capacity: int,
    ) -> None:
        """Создать локацию.

        capacity — максимальное число членов съёмочной группы.
        """
        if not Location.validate_capacity(capacity):
            raise ValueError("Вместимость должна быть положительным числом")
        super().__init__(location_id)
        self.name = name
        self.address = address
        self.capacity = capacity

    @staticmethod
    def validate_capacity(capacity: int) -> bool:
        """Проверить корректность значения вместимости."""
        return isinstance(capacity, int) and capacity > 0

    @classmethod
    def from_data(cls, data: dict) -> "Location":
        """Создать локацию из словаря, прочитанного из JSON."""
        return cls(data["id"], data["name"], data["address"],
                   data["capacity"])

    def is_suitable_for(self, crew_size: int) -> bool:
        """Проверить, вмещает ли локация группу из crew_size человек."""
        return self.capacity >= crew_size

    def to_data(self) -> dict:
        """Вернуть данные локации для записи в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "capacity": self.capacity,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление локации."""
        return f"{self.name} ({self.address}), до {self.capacity} чел."


def add_location(
    locations: List[Location],
    name: str,
    address: str,
    capacity: int,
) -> Location:
    """Создать локацию, добавить её в коллекцию и вернуть."""
    location_id = max((loc.id for loc in locations), default=0) + 1
    location = Location(location_id, name, address, capacity)
    locations.append(location)
    return location


def find_location(locations: List[Location], query: str) -> List[Location]:
    """Найти локации, в названии которых встречается подстрока query."""
    query = query.lower()
    return [loc for loc in locations if query in loc.name.lower()]


def find_location_by_id(
    locations: List[Location],
    location_id: int,
) -> Optional[Location]:
    """Найти локацию по идентификатору; вернуть None, если её нет."""
    for location in locations:
        if location.id == location_id:
            return location
    return None


def check_location_capacity(
    locations: List[Location],
    location_id: int,
    crew_size: int,
) -> bool:
    """Найти локацию и проверить, вмещает ли она группу.

    Если локации с таким идентификатором нет, возбуждается KeyError.
    """
    location = find_location_by_id(locations, location_id)
    if location is None:
        raise KeyError(f"Локация с id={location_id} не найдена")
    return location.is_suitable_for(crew_size)


def filter_locations_by_capacity(
    locations: List[Location],
    min_capacity: int,
) -> Iterator[Location]:
    """Отобрать локации, вмещающие не меньше min_capacity человек.

    Функция-генератор: подходящие локации выдаются по одной.
    """
    for location in locations:
        if location.is_suitable_for(min_capacity):
            yield location


def sort_locations(
    locations: List[Location],
    reverse: bool = False,
) -> List[Location]:
    """Вернуть локации, упорядоченные по вместимости."""
    return sorted(locations, key=lambda loc: loc.capacity, reverse=reverse)


def show_locations(locations: List[Location]) -> None:
    """Вывести список локаций."""
    if not locations:
        print("Локаций нет.")
        return
    for location in locations:
        print(f"[{location.id}] {location}")
