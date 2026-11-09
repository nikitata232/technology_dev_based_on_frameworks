from django.urls import path

from . import views

app_name = "locations"

urlpatterns = [
    path("place/<slug:slug>/", views.location_detail, name="detail_slug"),
    path("", views.locations, name="list"),
    path("free/", views.free_locations, name="free"),
    path("<int:location_id>/", views.location_detail, name="detail"),
]
