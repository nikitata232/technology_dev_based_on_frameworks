"""Классы Film и Scene и функции работы с коллекцией фильмов."""
from typing import List, Optional

from .base import Entity


class Scene:
    """Сцена фильма.

    Сцена не существует отдельно от фильма, поэтому идентифицируется
    номером внутри фильма и хранится в его списке scenes (композиция).
    """

    def __init__(self, number: int, description: str, crew_size: int) -> None:
        """Создать сцену; crew_size — размер нужной съёмочной группы."""
        if crew_size <= 0:
            raise ValueError("Размер группы должен быть положительным числом")
        self.number = number
        self.description = description
        self.crew_size = crew_size

    @classmethod
    def from_data(cls, data: dict) -> "Scene":
        """Создать сцену из словаря, прочитанного из JSON."""
        return cls(data["number"], data["description"], data["crew_size"])

    def to_data(self) -> dict:
        """Вернуть данные сцены для записи в JSON."""
        return {
            "number": self.number,
            "description": self.description,
            "crew_size": self.crew_size,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление сцены."""
        return (f"Сцена №{self.number}: {self.description} "
                f"(группа {self.crew_size} чел.)")


class Film(Entity):
    """Фильм со списком сцен."""

    def __init__(
        self,
        film_id: int,
        title: str,
        director: str,
        scenes: Optional[List[Scene]] = None,
    ) -> None:
        """Создать фильм."""
        if not title.strip():
            raise ValueError("Название фильма не может быть пустым")
        super().__init__(film_id)
        self.title = title
        self.director = director
        self.scenes: List[Scene] = scenes if scenes is not None else []

    @classmethod
    def from_data(cls, data: dict) -> "Film":
        """Создать фильм вместе со сценами из словаря JSON."""
        scenes = [Scene.from_data(item) for item in data.get("scenes", [])]
        return cls(data["id"], data["title"], data["director"], scenes)

    def add_scene(self, description: str, crew_size: int) -> Scene:
        """Добавить к фильму новую сцену и вернуть её."""
        number = max((s.number for s in self.scenes), default=0) + 1
        scene = Scene(number, description, crew_size)
        self.scenes.append(scene)
        return scene

    def get_scene(self, number: int) -> Optional[Scene]:
        """Вернуть сцену по номеру или None, если её нет."""
        for scene in self.scenes:
            if scene.number == number:
                return scene
        return None

    def to_data(self) -> dict:
        """Вернуть данные фильма со сценами для записи в JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "director": self.director,
            "scenes": [scene.to_data() for scene in self.scenes],
        }

    def __str__(self) -> str:
        """Вернуть строковое представление фильма."""
        return f"«{self.title}», реж. {self.director}"


def add_film(films: List[Film], title: str, director: str) -> Film:
    """Создать фильм, добавить его в коллекцию и вернуть."""
    film_id = max((film.id for film in films), default=0) + 1
    film = Film(film_id, title, director)
    films.append(film)
    return film


def find_film(films: List[Film], query: str) -> List[Film]:
    """Найти фильмы, в названии которых встречается подстрока query."""
    query = query.lower()
    return [film for film in films if query in film.title.lower()]


def find_film_by_id(films: List[Film], film_id: int) -> Optional[Film]:
    """Найти фильм по идентификатору; вернуть None, если его нет."""
    for film in films:
        if film.id == film_id:
            return film
    return None


def show_films(films: List[Film]) -> None:
    """Вывести фильмы и их сцены."""
    if not films:
        print("Фильмов нет.")
        return
    for film in films:
        print(f"[{film.id}] {film}")
        for scene in film.scenes:
            print(f"    {scene}")
