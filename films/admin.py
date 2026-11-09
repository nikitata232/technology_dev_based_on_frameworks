"""Фильмы, сцены и редактирование состава фильма."""
from django.contrib import admin
from django.db.models import Count

from .models import Film, Scene


class SceneInline(admin.TabularInline):
    model = Scene
    extra = 0
    fields = ("number", "description", "crew_size")
    show_change_link = True


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "director", "scene_count")
    search_fields = ("title", "director")
    ordering = ("title", "pk")
    readonly_fields = ("id",)
    inlines = (SceneInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            scene_total=Count("scenes"),
        )

    @admin.display(description="Сцен", ordering="scene_total")
    def scene_count(self, obj):
        return obj.scene_total


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ("id", "film", "number", "description", "crew_size")
    list_filter = ("film",)
    search_fields = ("film__title", "description")
    list_select_related = ("film",)
    ordering = ("film__title", "number", "pk")
    readonly_fields = ("id",)
