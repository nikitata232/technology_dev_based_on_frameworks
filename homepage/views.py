"""Главная страница и общий HTML-каркас всех страниц проекта."""
from django.http import HttpRequest, HttpResponse

from storage import load_films, load_locations, load_shootings

BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
    "/dist/css/bootstrap.min.css"
)


def page(title: str, content: str) -> str:
    """Собрать HTML-документ: кодировка, Bootstrap, навигация и content."""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{BOOTSTRAP_CSS}">
</head>
<body>
    <nav class="navbar navbar-expand bg-dark mb-4" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand" href="/">КиноПлан</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/films/">Фильмы</a>
                <a class="nav-link" href="/locations/">Локации</a>
                <a class="nav-link" href="/shootings/">График съёмок</a>
            </div>
        </div>
    </nav>
    <main class="container mb-5">{content}</main>
</body>
</html>"""


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание сервиса и навигация по разделам."""
    films = load_films()
    locations = load_locations()
    shootings = load_shootings(films, locations)
    active = [s for s in shootings if not s.is_cancelled]
    content = f"""
    <h1 class="display-5">КиноПлан</h1>
    <p class="lead">Сервис планирования киносъёмок: фильмы и сцены,
    локации и график съёмок с контролем занятости локаций.</p>
    <div class="row g-3 my-3">
        <div class="col-sm-4"><div class="card text-center"><div
            class="card-body"><div class="fs-2">{len(films)}</div>
            фильмов</div></div></div>
        <div class="col-sm-4"><div class="card text-center"><div
            class="card-body"><div class="fs-2">{len(locations)}</div>
            локаций</div></div></div>
        <div class="col-sm-4"><div class="card text-center"><div
            class="card-body"><div class="fs-2">{len(active)}</div>
            активных съёмок</div></div></div>
    </div>
    <a href="/films/" class="btn btn-primary me-2">Фильмы</a>
    <a href="/locations/" class="btn btn-secondary me-2">Локации</a>
    <a href="/shootings/" class="btn btn-outline-dark">График съёмок</a>
    """
    return HttpResponse(page("КиноПлан", content))


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Собственная страница ошибки 404 (подключена в handler404)."""
    content = """
    <h1 class="text-danger">404 — страница не найдена</h1>
    <p>Проверьте адрес или вернитесь на главную.</p>
    <a href="/" class="btn btn-primary">На главную</a>
    """
    return HttpResponse(
        page("404 — страница не найдена", content),
        status=404,
    )


def not_found_page(title: str, back_url: str, back_text: str) -> str:
    """Собрать страницу «объект не найден» со ссылкой назад."""
    content = f"""
    <h1 class="text-danger">{title}</h1>
    <a href="{back_url}" class="btn btn-outline-secondary">← {back_text}</a>
    """
    return page(title, content)
