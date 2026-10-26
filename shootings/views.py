"""Страницы графика съёмок."""
from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.views import not_found_page, page
from models import Shooting
from models.shootings import find_shooting_by_id, sort_shootings
from storage import load_films, load_locations, load_shootings


def status_badge(shooting: Shooting) -> str:
    """Вернуть HTML-бейдж статуса съёмки."""
    if shooting.is_cancelled:
        color = "bg-secondary"
    elif shooting.days_until() < 0:
        color = "bg-dark"
    else:
        color = "bg-success"
    return f'<span class="badge {color}">{shooting.status}</span>'


def shootings(request: HttpRequest) -> HttpResponse:
    """Страница /shootings/: график съёмок по датам."""
    shootings_list = load_shootings(load_films(), load_locations())
    rows = ""
    for shooting in sort_shootings(shootings_list):
        rows += f"""
        <tr>
            <td><a href="/shootings/{shooting.id}/">
                {shooting.shooting_date.strftime("%d.%m.%Y")}</a></td>
            <td>{escape(shooting.film.title)}</td>
            <td>№{shooting.scene.number}</td>
            <td>{escape(shooting.location.name)}</td>
            <td>{status_badge(shooting)}</td>
        </tr>"""
    content = f"""
    <h1>График съёмок</h1>
    <table class="table table-hover align-middle">
        <thead><tr><th>Дата</th><th>Фильм</th><th>Сцена</th>
            <th>Локация</th><th>Статус</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """
    return HttpResponse(page("КиноПлан — график съёмок", content))


def shooting_detail(request: HttpRequest, shooting_id: int) -> HttpResponse:
    """Страница /shootings/<id>/: карточка съёмки со связанными объектами."""
    shootings_list = load_shootings(load_films(), load_locations())
    shooting = find_shooting_by_id(shootings_list, shooting_id)
    if shooting is None:
        return HttpResponse(
            not_found_page(
                "Съёмка не найдена", "/shootings/", "к графику съёмок"
            ),
            status=404,
        )
    film, scene, location = shooting.film, shooting.scene, shooting.location
    content = f"""
    <div class="card">
        <div class="card-body">
            <h4 class="card-title">Съёмка №{shooting.id}</h4>
            <p class="card-text"><strong>Дата:</strong>
                {shooting.shooting_date.strftime("%d.%m.%Y")}</p>
            <p class="card-text"><strong>Фильм:</strong>
                <a href="/films/{film.id}/">{escape(film)}</a></p>
            <p class="card-text"><strong>Сцена:</strong>
                {escape(scene)}</p>
            <p class="card-text"><strong>Локация:</strong>
                <a href="/locations/{location.id}/">
                {escape(location)}</a></p>
            <p class="card-text"><strong>Статус:</strong>
                {status_badge(shooting)}</p>
            <a href="/shootings/" class="btn btn-outline-secondary">
                ← к графику съёмок</a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Съёмка №{shooting.id}", content))
