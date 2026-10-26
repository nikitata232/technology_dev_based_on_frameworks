"""Страницы локаций и проверка их доступности на дату."""
from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.locations import find_location_by_id, sort_locations
from models.shootings import (
    check_location_availability,
    is_location_available,
    sort_shootings,
)
from storage import load_films, load_locations, load_shootings


def locations(request: HttpRequest) -> HttpResponse:
    """Страница /locations/: таблица локаций по убыванию вместимости."""
    context = {
        "locations": sort_locations(load_locations(), reverse=True),
    }
    return render(request, "locations/location_list.html", context)


def location_detail(request: HttpRequest, location_id: int) -> HttpResponse:
    """Страница /locations/<id>/: карточка локации и её занятость.

    Дату проверки можно передать GET-параметром ?date=ГГГГ-ММ-ДД,
    по умолчанию проверяется текущая дата.
    """
    locations_list = load_locations()
    location = find_location_by_id(locations_list, location_id)
    if location is None:
        return render(
            request,
            "locations/location_detail.html",
            {"location": None},
            status=404,
        )
    shootings = load_shootings(load_films(), locations_list)

    bad_date = False
    try:
        check_date = date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        check_date = date.today()
        bad_date = "date" in request.GET

    available = is_location_available(shootings, location, check_date)
    context = {
        "location": location,
        "check_date": check_date,
        "bad_date": bad_date,
        "available": available,
        "availability": check_location_availability(not available),
        "location_shootings": [
            s for s in sort_shootings(shootings) if s.location is location
        ],
    }
    return render(request, "locations/location_detail.html", context)
