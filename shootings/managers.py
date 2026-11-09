"""Повторно используемые цепочки ORM для графика и административной панели."""
from django.db import models
from django.db.models import F, Q


class ShootingQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status="active")

    def cancelled(self):
        return self.filter(status="cancelled")

    def completed(self):
        return self.filter(status="completed")

    def on_date(self, value):
        return self.filter(shooting_date=value)

    def with_related(self):
        return self.select_related("scene__film", "location")

    def search(self, text):
        return self.filter(
            Q(scene__film__title__icontains=text)
            | Q(location__name__icontains=text)
            | Q(scene__description__icontains=text)
        )

    def with_capacity_margin(self):
        return self.annotate(
            capacity_margin=F("location__capacity") - F("scene__crew_size"),
        )


class ShootingManager(models.Manager.from_queryset(ShootingQuerySet)):
    """Методы QuerySet доступны и на Shooting.objects, и в цепочках."""
