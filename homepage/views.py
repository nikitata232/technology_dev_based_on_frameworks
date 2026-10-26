"""Главная страница и собственная страница ошибки 404."""
from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db import queries


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: сводка по базе данных и ближайшие съёмки."""
    context = {
        "summary": queries.get_summary(),
        "upcoming_shootings": queries.get_upcoming_shootings(date.today()),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Собственная страница ошибки 404 (подключена в handler404)."""
    return render(request, "homepage/404.html", status=404)
