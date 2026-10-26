"""Страницы локаций, проверка занятости и поиск свободных локаций.

Данные берутся из SQLite (db/queries.py).
"""
from datetime import date
from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db import queries
from models.shootings import check_location_availability


def parse_positive_int(value: str) -> Optional[int]:
    """Преобразовать строку из GET-параметра в целое > 0 или вернуть None."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def locations(request: HttpRequest) -> HttpResponse:
    """Страница /locations/: локации, при ?capacity=N — вмещающие N чел."""
    min_capacity = parse_positive_int(request.GET.get("capacity"))
    context = {
        "locations": queries.get_locations(min_capacity or 0),
        "min_capacity": min_capacity,
        "bad_capacity": "capacity" in request.GET and min_capacity is None,
    }
    return render(request, "locations/location_list.html", context)


def location_detail(request: HttpRequest, location_id: int) -> HttpResponse:
    """Страница /locations/<id>/: карточка локации и её занятость.

    Дату проверки можно передать GET-параметром ?date=ГГГГ-ММ-ДД,
    по умолчанию проверяется текущая дата.
    """
    location = queries.get_location(location_id)
    if location is None:
        return render(
            request,
            "locations/location_detail.html",
            {"location": None},
            status=404,
        )

    bad_date = False
    try:
        check_date = date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        check_date = date.today()
        bad_date = "date" in request.GET

    is_busy = queries.is_location_busy(location_id, check_date)
    context = {
        "location": location,
        "check_date": check_date,
        "bad_date": bad_date,
        "available": not is_busy,
        "availability": check_location_availability(is_busy),
        "location_shootings": queries.get_location_shootings(location_id),
    }
    return render(request, "locations/location_detail.html", context)


def free_locations(request: HttpRequest) -> HttpResponse:
    """Страница /locations/free/: локации, свободные на дату.

    GET-параметры: date=ГГГГ-ММ-ДД (обязателен для поиска) и
    crew=N — размер съёмочной группы (по умолчанию 1).
    """
    raw_date = request.GET.get("date", "")
    crew_size = parse_positive_int(request.GET.get("crew")) or 1
    check_date = None
    error = ""
    if raw_date:
        try:
            check_date = date.fromisoformat(raw_date)
        except ValueError:
            error = "Некорректная дата. Используйте формат ГГГГ-ММ-ДД."

    context = {
        "check_date": check_date,
        "crew_size": crew_size,
        "error": error,
        "locations": (
            queries.find_free_locations(check_date, crew_size)
            if check_date else []
        ),
    }
    return render(request, "locations/free_locations.html", context)
