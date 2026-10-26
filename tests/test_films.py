import pytest

from models import Film, Scene
from models.films import add_film, find_film, find_film_by_id


def test_film_creation_and_add_scene():
    film = Film(1, "Полночный экспресс", "А. Сергеев")
    scene = film.add_scene("Прибытие поезда", 35)
    assert isinstance(scene, Scene)
    assert scene.number == 1
    assert film.get_scene(1) is scene
    assert film.get_scene(5) is None


def test_scene_str():
    scene = Scene(2, "Разговор в купе", 10)
    assert str(scene) == "Сцена №2: Разговор в купе (группа 10 чел.)"


def test_film_from_data_restores_scenes():
    data = {
        "id": 3, "title": "Фильм", "director": "Режиссёр",
        "scenes": [{"number": 1, "description": "Сцена", "crew_size": 5}],
    }
    film = Film.from_data(data)
    assert film.id == 3
    assert film.scenes[0].crew_size == 5
    assert film.to_data() == data


def test_empty_title_forbidden():
    with pytest.raises(ValueError):
        Film(1, "  ", "Режиссёр")


def test_add_and_find_film():
    films = []
    film = add_film(films, "Полночный экспресс", "А. Сергеев")
    assert find_film(films, "экспресс") == [film]
    assert find_film_by_id(films, 1) is film
    assert find_film_by_id(films, 2) is None
