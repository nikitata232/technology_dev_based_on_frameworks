"""Общие данные, используемые каркасом сайта."""
from locations.models import Location


def site_context(request):
    return {
        "site_name": "КиноПлан",
        "site_locations_count": Location.objects.count(),
    }
