from django.urls import path

from . import views

urlpatterns = [
    path("", views.locations, name="locations"),
    path(
        "<int:location_id>/",
        views.location_detail,
        name="location_detail",
    ),
]
