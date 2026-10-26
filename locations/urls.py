from django.urls import path

from . import views

app_name = "locations"

urlpatterns = [
    path("", views.locations, name="list"),
    path("<int:location_id>/", views.location_detail, name="detail"),
]
