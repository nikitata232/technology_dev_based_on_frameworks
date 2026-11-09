"""Фильмы и сцены в базе Django."""
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Film(models.Model):
    title = models.CharField("Название", max_length=200)
    director = models.CharField("Режиссёр", max_length=150, blank=True)

    class Meta:
        ordering = ("title", "pk")
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("films:detail", args=[self.pk])


class Scene(models.Model):
    film = models.ForeignKey(
        Film, on_delete=models.CASCADE, related_name="scenes",
        verbose_name="Фильм",
    )
    number = models.PositiveIntegerField(
        "Номер сцены", validators=[MinValueValidator(1)],
    )
    description = models.TextField("Описание")
    crew_size = models.PositiveIntegerField(
        "Размер группы", validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ("film_id", "number")
        verbose_name = "Сцена"
        verbose_name_plural = "Сцены"
        constraints = [
            models.UniqueConstraint(
                fields=("film", "number"), name="unique_film_scene_number",
            ),
            models.CheckConstraint(
                condition=models.Q(crew_size__gt=0), name="positive_crew_size",
            ),
            models.CheckConstraint(
                condition=models.Q(number__gt=0), name="positive_scene_number",
            ),
        ]

    def __str__(self):
        return f"{self.film} — сцена №{self.number}"
