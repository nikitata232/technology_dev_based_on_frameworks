"""Демонстрация CRUD и ORM без сохранения учебных записей."""
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F

from db import queries
from films.models import Film, Scene
from locations.models import Location
from shootings.services import (
    cancel_shooting, delete_cancelled_shooting, reschedule_shooting,
    schedule_shooting,
)


class Command(BaseCommand):
    help = "Проверить CRUD с откатом учебных данных."

    @transaction.atomic
    def handle(self, *args, **options):
        film = Film.objects.create(title="Проверка ORM")
        scene = Scene.objects.create(
            film=film, number=1, description="Учебная сцена", crew_size=5,
        )
        location = Location.objects.create(name="Учебная локация", capacity=10)
        shooting = schedule_shooting(
            scene=scene, location=location, shooting_date=date(2030, 1, 1),
        )
        reschedule_shooting(shooting, date(2030, 1, 2))
        Location.objects.filter(pk=location.pk).update(
            capacity=F("capacity") + 1,
        )
        cancel_shooting(shooting)
        delete_cancelled_shooting(shooting)
        scene.delete()
        film.delete()
        location.delete()
        self.stdout.write(f"Итоги: {queries.get_shooting_totals()}")
        self.stdout.write(
            "CRUD: создание, чтение, изменение, отмена и удаление — OK. "
            "F-выражение — OK. Учебные изменения отменены.",
        )
        transaction.set_rollback(True)
