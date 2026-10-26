from django.urls import path

from . import views

urlpatterns = [
    path("", views.shootings, name="shootings"),
    path(
        "<int:shooting_id>/",
        views.shooting_detail,
        name="shooting_detail",
    ),
]
