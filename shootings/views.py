"""Страницы графика съёмок и статистики (данные из SQLite)."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db import queries

DEFAULT_MIN_SHOOTINGS = 2


def shootings(request: HttpRequest) -> HttpResponse:
    """Страница /shootings/: график съёмок по датам."""
    context = {
        "shootings": queries.get_shootings(),
    }
    return render(request, "shootings/shooting_list.html", context)


def shooting_detail(request: HttpRequest, shooting_id: int) -> HttpResponse:
    """Страница /shootings/<id>/: карточка съёмки со связанными данными."""
    shooting = queries.get_shooting(shooting_id)
    context = {
        "shooting": shooting,
    }
    return render(
        request,
        "shootings/shooting_detail.html",
        context,
        status=404 if shooting is None else 200,
    )


def statistics(request: HttpRequest) -> HttpResponse:
    """Страница /shootings/statistics/: агрегаты и группировки.

    Порог «загруженных» локаций задаётся GET-параметром ?min=N
    и передаётся в запрос с HAVING параметром.
    """
    try:
        min_count = max(int(request.GET.get("min", "")), 1)
    except ValueError:
        min_count = DEFAULT_MIN_SHOOTINGS
    context = {
        "totals": queries.get_shooting_totals(),
        "location_stats": queries.get_location_statistics(),
        "film_stats": queries.get_film_statistics(),
        "busy_locations": queries.get_busy_locations(min_count),
        "min_count": min_count,
        "by_month": queries.get_shootings_by_month(),
        "unscheduled_scenes": queries.get_unscheduled_scenes(),
    }
    return render(request, "shootings/statistics.html", context)
