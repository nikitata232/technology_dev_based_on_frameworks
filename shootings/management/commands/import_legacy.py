"""Перенос базы ПР7 в ORM с сохранением источника."""
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from films.models import Film, Scene
from locations.models import Location
from shootings.models import Shooting


class Command(BaseCommand):
    help = "Перенос SQLite ПР7 в пустую базу ORM."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source", type=Path,
            default=settings.BASE_DIR / "data" / "kinoplan.sqlite",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        source = Path(options["source"]).resolve()
        if any(model.objects.exists() for model in (
            Film, Scene, Location, Shooting,
        )):
            raise CommandError("Таблицы ORM уже содержат данные.")
        if not source.is_file():
            raise CommandError(f"Файл не найден: {source}")
        # Raw SQL разрешён только на границе переноса старого формата.
        conn = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            for row in conn.execute("SELECT * FROM films"):
                Film.objects.create(
                    id=row["id"], title=row["title"],
                    director=row["director"] or "",
                )
            for row in conn.execute("SELECT * FROM locations"):
                Location.objects.create(
                    id=row["id"], name=row["name"],
                    address=row["address"] or "", capacity=row["capacity"],
                )
            for row in conn.execute("SELECT * FROM scenes"):
                Scene.objects.create(**dict(row))
            for row in conn.execute("SELECT * FROM shootings"):
                Shooting.objects.create(**dict(row))
        except (sqlite3.Error, KeyError) as error:
            raise CommandError(f"Ошибка источника: {error}") from error
        finally:
            conn.close()
        self.stdout.write(self.style.SUCCESS(
            f"Перенесено: фильмов {Film.objects.count()}, "
            f"сцен {Scene.objects.count()}, "
            f"локаций {Location.objects.count()}, "
            f"съёмок {Shooting.objects.count()}. Источник сохранён.",
        ))
