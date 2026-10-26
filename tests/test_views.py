"""Тесты страниц веб-интерфейса (ПР5): URL → view → response."""
import pytest
from django.test import Client, override_settings


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
