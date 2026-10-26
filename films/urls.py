from django.urls import path

from . import views

app_name = "films"

urlpatterns = [
    path("", views.films, name="list"),
    path("<int:film_id>/", views.film_detail, name="detail"),
]
