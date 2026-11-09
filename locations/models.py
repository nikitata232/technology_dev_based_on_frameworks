"""Локации киносъёмок."""
from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from .slugs import location_slug


class LocationQuerySet(models.QuerySet):
    def available_on(self, value):
        from shootings.models import Shooting
        busy = Shooting.objects.active().on_date(value).values("location_id")
        return self.exclude(pk__in=busy)


class Location(models.Model):
    objects = LocationQuerySet.as_manager()
    slug = models.SlugField("Адрес страницы", max_length=200, unique=True,
                            blank=True)
    is_large = models.GeneratedField(
        expression=models.Case(
            models.When(capacity__gte=50, then=models.Value(True)),
            default=models.Value(False), output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(), db_persist=True,
        verbose_name="Большая локация",
    )
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{location_slug(self.name)}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("locations:detail_slug", args=[self.slug])
