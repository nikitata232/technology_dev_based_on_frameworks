"""Съёмки и ограничения предметной области."""
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from models.shootings import get_status_text


class Shooting(models.Model):
    scene = models.ForeignKey(
        "films.Scene", on_delete=models.PROTECT, related_name="shootings",
        verbose_name="Сцена",
    )
    location = models.ForeignKey(
        "locations.Location", on_delete=models.PROTECT,
        related_name="shootings", verbose_name="Локация",
    )
    shooting_date = models.DateField("Дата съёмки")
    is_cancelled = models.BooleanField("Отменена", default=False)

    class Meta:
        ordering = ("shooting_date", "pk")
        verbose_name = "Съёмка"
        verbose_name_plural = "Съёмки"
        constraints = [
            models.UniqueConstraint(
                fields=("location", "shooting_date"),
                condition=models.Q(is_cancelled=False),
                name="unique_active_location_date",
                violation_error_message="Локация уже занята на эту дату.",
            ),
        ]

    def clean(self):
        super().clean()
        if (self.scene_id and self.location_id
                and self.scene.crew_size > self.location.capacity):
            raise ValidationError({"location": "Локация не вмещает группу."})

    @property
    def days_until(self):
        return (self.shooting_date - timezone.localdate()).days

    @property
    def status(self):
        return get_status_text(self.is_cancelled, self.days_until)

    @property
    def film_id(self):
        return self.scene.film_id

    @property
    def film_title(self):
        return self.scene.film.title

    @property
    def film_director(self):
        return self.scene.film.director

    @property
    def scene_number(self):
        return self.scene.number

    @property
    def scene_description(self):
        return self.scene.description

    @property
    def crew_size(self):
        return self.scene.crew_size

    @property
    def location_name(self):
        return self.location.name

    @property
    def location_address(self):
        return self.location.address

    @property
    def location_capacity(self):
        return self.location.capacity

    def get_absolute_url(self):
        return reverse("shootings:detail", args=[self.pk])

    def __str__(self):
        return (f"{self.shooting_date:%d.%m.%Y} — "
                f"{self.scene} — {self.location}")
