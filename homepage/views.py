"""Главная страница и собственная страница ошибки 404."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.shootings import sort_shootings
from storage import load_films, load_locations, load_shootings


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: сводка по данным и ближайшие съёмки."""
    films = load_films()
    locations = load_locations()
    shootings = sort_shootings(load_shootings(films, locations))
    active_shootings = [s for s in shootings if not s.is_cancelled]
    context = {
        "films": films,
        "locations": locations,
        "active_shootings": active_shootings,
        "upcoming_shootings": [
            s for s in active_shootings if s.days_until() >= 0
        ],
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Собственная страница ошибки 404 (подключена в handler404)."""
    return render(request, "homepage/404.html", status=404)
