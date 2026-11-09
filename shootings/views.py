"""Страницы графика съёмок и статистики (Django ORM)."""
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db import queries

DEFAULT_MIN_SHOOTINGS = 2


def shootings(request: HttpRequest) -> HttpResponse:
    """Страница /shootings/: график съёмок по датам."""
    queryset = queries.get_shootings()
    search = request.GET.get("q", "").strip()[:200]
    if search:
        queryset = queryset.search(search)
    errors = []
    for key, field in (
        ("film", "scene__film_id"), ("location", "location_id"),
    ):
        raw = request.GET.get(key, "")
        if raw:
            try:
                value = int(raw)
                if value < 1:
                    raise ValueError
            except ValueError:
                errors.append("Некорректный идентификатор фильтра.")
            else:
                queryset = queryset.filter(**{field: value})
    state = request.GET.get("status", "")
    if state in ("active", "cancelled", "completed"):
        queryset = queryset.filter(status=state)
    elif state:
        errors.append("Неизвестный статус.")
    raw_date = request.GET.get("date", "")
    if raw_date:
        from datetime import date
        try:
            queryset = queryset.filter(
                shooting_date=date.fromisoformat(raw_date),
            )
        except ValueError:
            errors.append("Некорректная дата.")
    orderings = {
        "date": ("shooting_date", "pk"),
        "-date": ("-shooting_date", "-pk"),
        "film": ("scene__film__title", "shooting_date", "pk"),
        "location": ("location__name", "shooting_date", "pk"),
    }
    sort = request.GET.get("sort", "date")
    if sort not in orderings:
        errors.append("Неизвестная сортировка; применена сортировка по дате.")
        sort = "date"
    queryset = queryset.order_by(*orderings[sort])
    page = Paginator(queryset, 5).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    context = {
        "shootings": page, "page_obj": page,
        "pagination_query": params.urlencode(),
        "search": search, "selected_status": state, "sort": sort,
        "filters": request.GET, "errors": errors,
        "films": queries.get_films(), "locations": queries.get_locations(),
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
    и применяется к аннотированному счётчику ORM.
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
