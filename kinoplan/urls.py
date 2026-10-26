"""Корневая маршрутизация проекта КиноПлан.

Адреса распределяются по приложениям функцией include():
часть адреса указывается здесь, остальное — в urls.py приложения.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("films/", include("films.urls")),
    path("locations/", include("locations.urls")),
    path("shootings/", include("shootings.urls")),
]

handler404 = "homepage.views.page_not_found"
