from django.urls import path

from . import views

app_name = "shootings"

urlpatterns = [
    path("", views.shootings, name="list"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:shooting_id>/", views.shooting_detail, name="detail"),
]
