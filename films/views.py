"""Страницы фильмов и их сцен."""
from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.views import not_found_page, page
from models.films import find_film_by_id
from models.shootings import sort_shootings
from storage import load_films, load_locations, load_shootings


def films(request: HttpRequest) -> HttpResponse:
    """Страница /films/: список фильмов."""
    items = ""
    for film in load_films():
        items += f"""
        <a href="/films/{film.id}/"
           class="list-group-item list-group-item-action
                  d-flex justify-content-between">
            <span>{escape(film)}</span>
            <span class="badge bg-primary">сцен: {len(film.scenes)}</span>
        </a>"""
    content = f"""
    <h1>Фильмы</h1>
    <div class="list-group">{items or "<p>Фильмов нет.</p>"}</div>
    """
    return HttpResponse(page("КиноПлан — фильмы", content))


def film_detail(request: HttpRequest, film_id: int) -> HttpResponse:
    """Страница /films/<id>/: сцены фильма и его съёмки."""
    films_list = load_films()
    film = find_film_by_id(films_list, film_id)
    if film is None:
        return HttpResponse(
            not_found_page("Фильм не найден", "/films/", "к списку фильмов"),
            status=404,
        )
    shootings = load_shootings(films_list, load_locations())

    scene_rows = ""
    for scene in film.scenes:
        scene_rows += f"""
        <tr><td>{scene.number}</td><td>{escape(scene.description)}</td>
            <td>{scene.crew_size}</td></tr>"""

    shooting_items = ""
    for shooting in sort_shootings(shootings):
        if shooting.film is film:
            shooting_items += f"""
            <a href="/shootings/{shooting.id}/"
               class="list-group-item list-group-item-action">
               {escape(shooting)}</a>"""

    content = f"""
    <h1>«{escape(film.title)}»</h1>
    <p class="text-muted">Режиссёр: {escape(film.director)}</p>
    <h4>Сцены</h4>
    <table class="table table-striped">
        <thead><tr><th>№</th><th>Описание</th><th>Группа, чел.</th></tr>
        </thead>
        <tbody>{scene_rows}</tbody>
    </table>
    <h4>Съёмки фильма</h4>
    <div class="list-group mb-3">
        {shooting_items or "<p>Съёмки ещё не назначены.</p>"}
    </div>
    <a href="/films/" class="btn btn-outline-secondary">← к списку фильмов</a>
    """
    return HttpResponse(page(film.title, content))
