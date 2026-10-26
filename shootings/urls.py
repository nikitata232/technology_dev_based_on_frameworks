from django.urls import path

from . import views

app_name = "shootings"

urlpatterns = [
    path("", views.shootings, name="list"),
    path("<int:shooting_id>/", views.shooting_detail, name="detail"),
]
