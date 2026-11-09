"""Локации киносъёмок."""
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Location(models.Model):
    name = models.CharField("Название", max_length=200)
    address = models.CharField("Адрес", max_length=250, blank=True)
    capacity = models.PositiveIntegerField(
        "Вместимость", validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ("-capacity", "name", "pk")
        verbose_name = "Локация"
        verbose_name_plural = "Локации"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity__gt=0), name="positive_capacity",
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("locations:detail", args=[self.pk])
