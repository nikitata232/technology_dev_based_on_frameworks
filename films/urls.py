from django.urls import path

from . import views

urlpatterns = [
    path("", views.films, name="films"),
    path("<int:film_id>/", views.film_detail, name="film_detail"),
]
