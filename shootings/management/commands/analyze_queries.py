"""Воспроизводимое сравнение запросов к связанным данным."""
from django.core.management.base import BaseCommand
from django.db import connection
from django.test import Client, override_settings
from django.test.utils import CaptureQueriesContext

from db.queries import get_shootings
from shootings.models import Shooting


class Command(BaseCommand):
    help = "Сравнить наивное чтение связей с select_related и показать SQL."

    def handle(self, *args, **options):
        with CaptureQueriesContext(connection) as before:
            original = [(s.scene.film.title, s.location.name)
                        for s in Shooting.objects.all()]
        with CaptureQueriesContext(connection) as after:
            optimized = [(s.scene.film.title, s.location.name)
                         for s in get_shootings()]
        self.stdout.write(
            f"Съёмок: {len(original)}; до: {len(before)}; "
            f"после: {len(after)}; данные равны: {original == optimized}",
        )
        if after:
            self.stdout.write(after[0]["sql"])
        with override_settings(ALLOWED_HOSTS=["testserver"]):
            with CaptureQueriesContext(connection) as page_queries:
                response = Client().get("/shootings/?q=е&sort=-date")
        self.stdout.write(
            f"Страница графика: HTTP {response.status_code}, "
            f"SQL-запросов: {len(page_queries)}",
        )
