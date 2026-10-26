"""Страницы фильмов и их сцен."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.films import find_film_by_id
from models.shootings import sort_shootings
from storage import load_films, load_locations, load_shootings


def films(request: HttpRequest) -> HttpResponse:
    """Страница /films/: список фильмов."""
    context = {
        "films": load_films(),
    }
    return render(request, "films/film_list.html", context)


def film_detail(request: HttpRequest, film_id: int) -> HttpResponse:
    """Страница /films/<id>/: сцены фильма и его съёмки."""
    films_list = load_films()
    film = find_film_by_id(films_list, film_id)
    film_shootings = []
    if film is not None:
        shootings = load_shootings(films_list, load_locations())
        film_shootings = [
            s for s in sort_shootings(shootings) if s.film is film
        ]
    context = {
        "film": film,
        "film_shootings": film_shootings,
    }
    return render(
        request,
        "films/film_detail.html",
        context,
        status=404 if film is None else 200,
    )
