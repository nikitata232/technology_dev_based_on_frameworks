"""Сервис планирования киносъёмок — консольная версия приложения."""
import inspect
from typing import List

import models.films as films_module
import models.locations as locations_module
import models.shootings as shootings_module
from models import Film, Location, Shooting
from models.films import add_film, find_film_by_id, show_films
from models.locations import (
    add_location,
    filter_locations_by_capacity,
    find_location,
    find_location_by_id,
    show_locations,
    sort_locations,
)
from models.shootings import (
    cancel_shooting,
    check_location_availability,
    create_shooting,
    is_location_available,
    show_shootings,
)
from storage import (
    load_films,
    load_locations,
    load_shootings,
    save_films,
    save_locations,
    save_shootings,
)
from utils import input_date, input_int, input_text

MENU = """
=== Сервис планирования киносъёмок ===
1. Показать локации
2. Найти локацию по названию
3. Добавить локацию
4. Подобрать локации по размеру группы
5. Показать фильмы и сцены
6. Добавить фильм
7. Добавить сцену к фильму
8. Проверить доступность локации на дату
9. Назначить съёмку
10. Отменить съёмку
11. Показать график съёмок
12. Справка по классам и функциям
0. Выход"""


def show_help() -> None:
    """Вывести справку по классам и функциям с помощью интроспекции."""
    for module in (locations_module, films_module, shootings_module):
        print(f"\nМодуль {module.__name__}:")
        members = inspect.getmembers(
            module,
            lambda obj: inspect.isfunction(obj) or inspect.isclass(obj),
        )
        for name, member in members:
            if member.__module__ != module.__name__:
                continue
            summary = (member.__doc__ or "").strip().splitlines()[0]
            kind = "класс" if inspect.isclass(member) else "функция"
            print(f"  {kind} {name}{inspect.signature(member)}")
            print(f"      {summary}")


def search_locations(locations: List[Location]) -> None:
    """Сценарий поиска локации по названию."""
    query = input_text("Часть названия: ")
    show_locations(find_location(locations, query))


def new_location(locations: List[Location]) -> None:
    """Сценарий добавления локации."""
    name = input_text("Название локации: ")
    address = input_text("Адрес: ")
    capacity = input_int("Вместимость (человек): ", min_value=1)
    location = add_location(locations, name, address, capacity)
    save_locations(locations)
    print(f"Локация добавлена, id={location.id}.")


def pick_locations(locations: List[Location]) -> None:
    """Сценарий подбора локаций по размеру съёмочной группы."""
    crew_size = input_int("Размер съёмочной группы: ", min_value=1)
    suitable = filter_locations_by_capacity(locations, crew_size)
    show_locations(sort_locations(list(suitable)))


def new_film(films: List[Film]) -> None:
    """Сценарий добавления фильма."""
    title = input_text("Название фильма: ")
    director = input_text("Режиссёр: ")
    film = add_film(films, title, director)
    save_films(films)
    print(f"Фильм добавлен, id={film.id}.")


def new_scene(films: List[Film]) -> None:
    """Сценарий добавления сцены к фильму."""
    film = find_film_by_id(films, input_int("ID фильма: "))
    if film is None:
        print("Фильм не найден.")
        return
    description = input_text("Описание сцены: ")
    crew_size = input_int("Размер группы (человек): ", min_value=1)
    scene = film.add_scene(description, crew_size)
    save_films(films)
    print(f"Добавлена {scene}.")


def check_availability(
    locations: List[Location],
    shootings: List[Shooting],
) -> None:
    """Сценарий проверки занятости локации на дату."""
    location = find_location_by_id(locations, input_int("ID локации: "))
    if location is None:
        print("Локация не найдена.")
        return
    shooting_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    is_free = is_location_available(shootings, location, shooting_date)
    print(check_location_availability(not is_free))


def create_new_shooting(
    shootings: List[Shooting],
    films: List[Film],
    locations: List[Location],
) -> None:
    """Сценарий назначения съёмки: поиск объектов и создание Shooting."""
    film = find_film_by_id(films, input_int("ID фильма: "))
    if film is None:
        print("Фильм не найден.")
        return
    scene = film.get_scene(input_int("Номер сцены: "))
    if scene is None:
        print("Сцена не найдена.")
        return
    location = find_location_by_id(locations, input_int("ID локации: "))
    if location is None:
        print("Локация не найдена.")
        return
    if not location.is_suitable_for(scene.crew_size):
        print("Локация не вмещает съёмочную группу этой сцены.")
        return
    shooting_date = input_date("Дата съёмки (ДД.ММ.ГГГГ): ")
    shooting = create_shooting(
        shootings, film, scene, location, shooting_date
    )
    if shooting is None:
        print(check_location_availability(True))
        return
    save_shootings(shootings)
    print(f"Съёмка назначена, id={shooting.id}.")
    print(shooting.status)


def remove_shooting(shootings: List[Shooting]) -> None:
    """Сценарий отмены съёмки."""
    if cancel_shooting(shootings, input_int("ID съёмки: ")):
        save_shootings(shootings)
        print("Съёмка отменена.")
    else:
        print("Активная съёмка с таким ID не найдена.")


def main() -> None:
    """Точка запуска: загрузка данных и цикл меню."""
    locations = load_locations()
    films = load_films()
    shootings = load_shootings(films, locations)

    actions = {
        "1": lambda: show_locations(locations),
        "2": lambda: search_locations(locations),
        "3": lambda: new_location(locations),
        "4": lambda: pick_locations(locations),
        "5": lambda: show_films(films),
        "6": lambda: new_film(films),
        "7": lambda: new_scene(films),
        "8": lambda: check_availability(locations, shootings),
        "9": lambda: create_new_shooting(shootings, films, locations),
        "10": lambda: remove_shooting(shootings),
        "11": lambda: show_shootings(shootings),
        "12": show_help,
    }

    while True:
        print(MENU)
        try:
            choice = input("Выберите действие: ").strip()
            if choice == "0":
                print("До свидания!")
                break
            action = actions.get(choice)
            if action is None:
                print("Нет такого пункта меню.")
                continue
            action()
        except (KeyboardInterrupt, EOFError):
            print("\nРабота завершена.")
            break


if __name__ == "__main__":
    main()
