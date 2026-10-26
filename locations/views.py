"""Страницы локаций и проверка их доступности на дату."""
from datetime import date

from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.views import not_found_page, page
from models.locations import find_location_by_id, sort_locations
from models.shootings import (
    check_location_availability,
    is_location_available,
    sort_shootings,
)
from storage import load_films, load_locations, load_shootings


def locations(request: HttpRequest) -> HttpResponse:
    """Страница /locations/: таблица локаций по убыванию вместимости."""
    rows = ""
    for location in sort_locations(load_locations(), reverse=True):
        rows += f"""
        <tr>
            <td><a href="/locations/{location.id}/">
                {escape(location.name)}</a></td>
            <td>{escape(location.address)}</td>
            <td>{location.capacity}</td>
        </tr>"""
    content = f"""
    <h1>Локации</h1>
    <table class="table table-hover">
        <thead><tr><th>Название</th><th>Адрес</th>
            <th>Вместимость, чел.</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """
    return HttpResponse(page("КиноПлан — локации", content))


def location_detail(request: HttpRequest, location_id: int) -> HttpResponse:
    """Страница /locations/<id>/: карточка локации и её занятость.

    Дату проверки можно передать GET-параметром ?date=ГГГГ-ММ-ДД,
    по умолчанию проверяется текущая дата.
    """
    locations_list = load_locations()
    location = find_location_by_id(locations_list, location_id)
    if location is None:
        return HttpResponse(
            not_found_page(
                "Локация не найдена", "/locations/", "к списку локаций"
            ),
            status=404,
        )
    shootings = load_shootings(load_films(), locations_list)

    warning = ""
    try:
        check_date = date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        check_date = date.today()
        if "date" in request.GET:
            warning = ('<div class="alert alert-warning">Некорректная '
                       'дата, показана текущая.</div>')

    available = is_location_available(shootings, location, check_date)
    badge = "bg-success" if available else "bg-danger"
    status = check_location_availability(not available)

    items = ""
    for shooting in sort_shootings(shootings):
        if shooting.location is location:
            items += f"""
            <a href="/shootings/{shooting.id}/"
               class="list-group-item list-group-item-action">
               {escape(shooting)}</a>"""

    content = f"""
    {warning}
    <div class="card mb-4">
        <div class="card-body">
            <h4 class="card-title">{escape(location.name)}</h4>
            <p class="card-text"><strong>ID:</strong> {location.id}</p>
            <p class="card-text"><strong>Адрес:</strong>
                {escape(location.address)}</p>
            <p class="card-text"><strong>Вместимость:</strong>
                {location.capacity} чел.</p>
            <form method="get" class="row g-2 align-items-center mb-2">
                <div class="col-auto">
                    <input type="date" name="date" class="form-control"
                           value="{check_date.isoformat()}">
                </div>
                <div class="col-auto">
                    <button class="btn btn-primary">Проверить дату</button>
                </div>
            </form>
            <p class="card-text">{check_date.strftime("%d.%m.%Y")}:
                <span class="badge {badge}">{status}</span></p>
        </div>
    </div>
    <h4>Съёмки на этой локации</h4>
    <div class="list-group mb-3">
        {items or "<p>Съёмок не назначено.</p>"}
    </div>
    <a href="/locations/" class="btn btn-outline-secondary">
        ← к списку локаций</a>
    """
    return HttpResponse(page(location.name, content))
