"""Класс Shooting и функции назначения, проверки и отмены съёмок."""
from datetime import date
from typing import List, Optional

from .base import Entity
from .films import Film, Scene
from .locations import Location


def check_location_availability(is_busy: bool) -> str:
    """Вернуть текстовый статус занятости локации (функция из ПР1)."""
    if is_busy:
        return "Локация занята на выбранную дату"
    return "Локация свободна для съёмки"


def get_days_until_shooting(
    shoot_date: date,
    today: Optional[date] = None,
) -> int:
    """Вернуть количество дней до съёмки (функция из ПР1)."""
    if today is None:
        today = date.today()
    delta = shoot_date - today
    return delta.days


def get_shooting_status(days_left: int) -> str:
    """Вернуть текстовый статус съёмки по числу дней (функция из ПР1)."""
    if days_left < 0:
        return "Съёмка уже прошла"
    elif days_left == 0:
        return "Съёмка сегодня"
    return f"До съёмки осталось {days_left} дн."


class Shooting(Entity):
    """Съёмка сцены фильма на локации в определённую дату.

    Съёмка хранит ссылки на объекты Film, Scene и Location,
    а не их идентификаторы (композиция объектов).
    """

    def __init__(
        self,
        shooting_id: int,
        film: Film,
        scene: Scene,
        location: Location,
        shooting_date: date,
        is_cancelled: bool = False,
    ) -> None:
        """Создать съёмку."""
        super().__init__(shooting_id)
        self.film = film
        self.scene = scene
        self.location = location
        self.shooting_date = shooting_date
        self._is_cancelled = is_cancelled

    @property
    def is_cancelled(self) -> bool:
        """Признак отмены; изменить его можно только методом cancel()."""
        return self._is_cancelled

    @property
    def status(self) -> str:
        """Текстовый статус съёмки с учётом отмены и даты."""
        if self._is_cancelled:
            return "Съёмка отменена"
        return get_shooting_status(self.days_until())

    def cancel(self) -> None:
        """Отменить съёмку.

        Объект остаётся в коллекции, но больше не блокирует локацию.
        """
        self._is_cancelled = True

    def days_until(self, today: Optional[date] = None) -> int:
        """Вернуть число дней до съёмки."""
        return get_days_until_shooting(self.shooting_date, today)

    def to_data(self) -> dict:
        """Вернуть данные съёмки для JSON: связи заменяются на id."""
        return {
            "id": self.id,
            "film_id": self.film.id,
            "scene_number": self.scene.number,
            "location_id": self.location.id,
            "shooting_date": self.shooting_date.isoformat(),
            "is_cancelled": self._is_cancelled,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление съёмки."""
        return (f"{self.shooting_date.strftime('%d.%m.%Y')} — "
                f"«{self.film.title}», сцена №{self.scene.number}, "
                f"{self.location.name}. {self.status}")


def is_location_available(
    shootings: List[Shooting],
    location: Location,
    shooting_date: date,
) -> bool:
    """Проверить, свободна ли локация на дату.

    Учитываются только активные съёмки: отменённая съёмка
    локацию не блокирует.
    """
    for shooting in shootings:
        if (not shooting.is_cancelled
                and shooting.location.id == location.id
                and shooting.shooting_date == shooting_date):
            return False
    return True


def create_shooting(
    shootings: List[Shooting],
    film: Film,
    scene: Scene,
    location: Location,
    shooting_date: date,
) -> Optional[Shooting]:
    """Назначить съёмку и добавить её в коллекцию.

    Если локация уже занята на эту дату, возвращается None.
    """
    if not is_location_available(shootings, location, shooting_date):
        return None
    shooting_id = max((s.id for s in shootings), default=0) + 1
    shooting = Shooting(shooting_id, film, scene, location, shooting_date)
    shootings.append(shooting)
    return shooting


def find_shooting_by_id(
    shootings: List[Shooting],
    shooting_id: int,
) -> Optional[Shooting]:
    """Найти съёмку по идентификатору; вернуть None, если её нет."""
    for shooting in shootings:
        if shooting.id == shooting_id:
            return shooting
    return None


def cancel_shooting(shootings: List[Shooting], shooting_id: int) -> bool:
    """Найти съёмку и отменить её методом cancel().

    Возвращает False, если съёмка не найдена или уже отменена.
    """
    shooting = find_shooting_by_id(shootings, shooting_id)
    if shooting is None or shooting.is_cancelled:
        return False
    shooting.cancel()
    return True


def sort_shootings(shootings: List[Shooting]) -> List[Shooting]:
    """Вернуть съёмки, упорядоченные по дате."""
    return sorted(shootings, key=lambda s: s.shooting_date)


def show_shootings(shootings: List[Shooting]) -> None:
    """Вывести график съёмок, упорядоченный по дате."""
    if not shootings:
        print("Съёмок не назначено.")
        return
    for shooting in sort_shootings(shootings):
        print(f"[{shooting.id}] {shooting}")
