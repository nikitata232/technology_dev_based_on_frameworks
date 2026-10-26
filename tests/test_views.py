"""Тесты страниц веб-интерфейса (ПР5–ПР6): URL → view → шаблон."""
import pytest
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import Client, override_settings
from django.urls import reverse

from homepage import views as homepage_views
from models import Film


@pytest.fixture
def client():
    return Client()


@pytest.mark.parametrize("url", [
    "/", "/films/", "/films/1/", "/locations/", "/locations/1/",
    "/shootings/", "/shootings/1/",
])
def test_pages_open(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert "bootstrap" in response.content.decode()


def test_location_page_shows_data(client):
    html = client.get("/locations/1/").content.decode()
    assert "Вокзал, павильон 3" in html
    assert "40 чел." in html


def test_location_busy_on_shooting_date(client):
    html = client.get("/locations/1/?date=2026-10-20").content.decode()
    assert "Локация занята на выбранную дату" in html


def test_location_bad_date_falls_back(client):
    html = client.get("/locations/1/?date=abc").content.decode()
    assert "Некорректная" in html


@pytest.mark.parametrize("url", [
    "/films/999/", "/locations/999/", "/shootings/999/",
])
def test_missing_objects_return_404(client, url):
    assert client.get(url).status_code == 404


def test_int_converter_rejects_text(client):
    assert client.get("/locations/abc/").status_code == 404


@override_settings(DEBUG=False)
def test_custom_404_page(client):
    response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "404 — страница не найдена" in response.content.decode()


# --- ПР6: шаблоны, include, url, фильтры, статика ---

def template_names(response):
    return [t.name for t in response.templates if t.name]


@pytest.mark.parametrize("url, template", [
    ("/", "homepage/index.html"),
    ("/films/", "films/film_list.html"),
    ("/films/1/", "films/film_detail.html"),
    ("/locations/", "locations/location_list.html"),
    ("/locations/1/", "locations/location_detail.html"),
    ("/shootings/", "shootings/shooting_list.html"),
    ("/shootings/1/", "shootings/shooting_detail.html"),
])
def test_pages_use_templates(client, url, template):
    names = template_names(client.get(url))
    assert template in names
    assert "base.html" in names
    assert "includes/navigation.html" in names


def test_includes_are_used(client):
    assert "films/includes/film_card.html" in template_names(
        client.get("/films/"))
    assert "shootings/includes/shooting_status.html" in template_names(
        client.get("/shootings/"))


def test_named_urls_with_namespaces():
    assert reverse("homepage:index") == "/"
    assert reverse("films:detail", args=[1]) == "/films/1/"
    assert reverse("locations:list") == "/locations/"
    assert reverse("shootings:detail", args=[2]) == "/shootings/2/"


def test_navigation_and_static_files(client):
    html = client.get("/").content.decode()
    for href in ('href="/films/"', 'href="/locations/"',
                 'href="/shootings/"'):
        assert href in html
    assert "/static/homepage/css/style.css" in html
    assert "/static/homepage/js/main.js" in html
    assert "/static/homepage/img/logo.png" in html


def test_static_files_found():
    for path in ("homepage/css/style.css", "homepage/js/main.js",
                 "homepage/img/logo.png"):
        assert finders.find(path) is not None


def test_shooting_statuses_rendered(client):
    html = client.get("/shootings/").content.decode()
    assert "kp-status-cancelled" in html
    assert "kp-status-active" in html
    assert "kp-status-past" in html


def test_date_filter(client):
    html = client.get("/shootings/1/").content.decode()
    assert "20.10.2026" in html


def test_empty_collections():
    html = render_to_string("films/film_list.html", {"films": []})
    assert "Фильмов нет." in html
    html = render_to_string("shootings/shooting_list.html",
                            {"shootings": []})
    assert "Съёмки ещё не назначены." in html


def test_default_filter():
    film = Film(5, "Тест", "")
    html = render_to_string("films/includes/film_card.html", {"film": film})
    assert "не указан" in html


def test_not_found_message_in_template(client):
    response = client.get("/films/999/")
    assert response.status_code == 404
    assert "Фильм не найден" in response.content.decode()
    assert "films/film_detail.html" in template_names(response)


def test_page_function_removed():
    assert not hasattr(homepage_views, "page")
