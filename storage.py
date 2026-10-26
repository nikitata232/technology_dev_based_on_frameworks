"""Загрузка и сохранение данных проекта в JSON-файлах.

В JSON хранятся обычные данные (словари и списки), а приложение
работает с объектами: здесь выполняется преобразование
JSON → объекты при загрузке и объекты → JSON при сохранении.
"""
import json
import os
from datetime import date
from typing import List, Sequence

from models import Film, Location, Shooting
from models.base import Entity
from models.films import find_film_by_id
from models.locations import find_location_by_id

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
LOCATIONS_FILE = os.path.join(DATA_DIR, "locations.json")
FILMS_FILE = os.path.join(DATA_DIR, "films.json")
SHOOTINGS_FILE = os.path.join(DATA_DIR, "shootings.json")


def load_json(filename: str) -> list:
    """Прочитать список записей из JSON-файла.

    Если файла нет или он повреждён, выводится предупреждение
    и возвращается пустой список — программа продолжает работу.
    """
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename} не найден, начинаем с пустых данных.")
        return []
    except json.JSONDecodeError:
        print(f"Файл {filename} повреждён, данные не загружены.")
        return []
    if not isinstance(data, list):
        print(f"Файл {filename} имеет неверный формат.")
        return []
    return data


def save_json(filename: str, data: list) -> None:
    """Записать список записей в JSON-файл."""
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except OSError as error:
        print(f"Не удалось сохранить {filename}: {error}")


def save_entities(filename: str, entities: Sequence[Entity]) -> None:
    """Сохранить любые сущности: каждая сама знает свой to_data()."""
    save_json(filename, [entity.to_data() for entity in entities])


def load_locations(filename: str = LOCATIONS_FILE) -> List[Location]:
    """Загрузить локации: JSON → объекты Location."""
    locations = []
    for data in load_json(filename):
        try:
            locations.append(Location.from_data(data))
        except (KeyError, ValueError):
            print(f"Пропущена некорректная запись локации: {data}")
    return locations


def save_locations(
    locations: List[Location],
    filename: str = LOCATIONS_FILE,
) -> None:
    """Сохранить локации: объекты Location → JSON."""
    save_entities(filename, locations)


def load_films(filename: str = FILMS_FILE) -> List[Film]:
    """Загрузить фильмы со сценами: JSON → объекты Film и Scene."""
    films = []
    for data in load_json(filename):
        try:
            films.append(Film.from_data(data))
        except (KeyError, ValueError):
            print(f"Пропущена некорректная запись фильма: {data}")
    return films


def save_films(films: List[Film], filename: str = FILMS_FILE) -> None:
    """Сохранить фильмы со сценами: объекты Film → JSON."""
    save_entities(filename, films)


def load_shootings(
    films: List[Film],
    locations: List[Location],
    filename: str = SHOOTINGS_FILE,
) -> List[Shooting]:
    """Загрузить съёмки и восстановить связи с объектами.

    По film_id, scene_number и location_id из JSON находятся
    объекты Film, Scene и Location. Если связанный объект не найден,
    съёмка не создаётся.
    """
    shootings = []
    for data in load_json(filename):
        try:
            film = find_film_by_id(films, data["film_id"])
            location = find_location_by_id(locations, data["location_id"])
            scene = film.get_scene(data["scene_number"]) if film else None
            if film is None or scene is None or location is None:
                raise LookupError
            shootings.append(Shooting(
                data["id"],
                film,
                scene,
                location,
                date.fromisoformat(data["shooting_date"]),
                data.get("is_cancelled", False),
            ))
        except (KeyError, ValueError, LookupError):
            print(f"Пропущена некорректная запись съёмки: {data}")
    return shootings


def save_shootings(
    shootings: List[Shooting],
    filename: str = SHOOTINGS_FILE,
) -> None:
    """Сохранить съёмки: ссылки на объекты заменяются на id."""
    save_entities(filename, shootings)
