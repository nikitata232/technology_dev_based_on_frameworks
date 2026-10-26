"""Страницы фильмов и их сцен (данные из SQLite)."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db import queries


def films(request: HttpRequest) -> HttpResponse:
    """Страница /films/: список фильмов с количеством сцен."""
    context = {
        "films": queries.get_films(),
    }
    return render(request, "films/film_list.html", context)


def film_detail(request: HttpRequest, film_id: int) -> HttpResponse:
    """Страница /films/<id>/: сцены фильма и его съёмки."""
    film = queries.get_film(film_id)
    context = {
        "film": film,
        "scenes": queries.get_scenes(film_id) if film else [],
        "film_shootings": (
            queries.get_film_shootings(film_id) if film else []
        ),
    }
    return render(
        request,
        "films/film_detail.html",
        context,
        status=404 if film is None else 200,
    )
