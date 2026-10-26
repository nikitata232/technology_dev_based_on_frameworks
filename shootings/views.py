"""Страницы графика съёмок."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.shootings import find_shooting_by_id, sort_shootings
from storage import load_films, load_locations, load_shootings


def shootings(request: HttpRequest) -> HttpResponse:
    """Страница /shootings/: график съёмок по датам."""
    shootings_list = load_shootings(load_films(), load_locations())
    context = {
        "shootings": sort_shootings(shootings_list),
    }
    return render(request, "shootings/shooting_list.html", context)


def shooting_detail(request: HttpRequest, shooting_id: int) -> HttpResponse:
    """Страница /shootings/<id>/: карточка съёмки со связанными объектами."""
    shootings_list = load_shootings(load_films(), load_locations())
    shooting = find_shooting_by_id(shootings_list, shooting_id)
    context = {
        "shooting": shooting,
    }
    return render(
        request,
        "shootings/shooting_detail.html",
        context,
        status=404 if shooting is None else 200,
    )
