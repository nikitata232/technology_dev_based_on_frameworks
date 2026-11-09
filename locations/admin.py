"""Локации, их съёмки и ссылка на публичную карточку."""
from django.contrib import admin

from shootings.admin import ShootingInline
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "address", "capacity", "large_location", "slug",
    )
    search_fields = ("name", "address")
    list_filter = ("is_large",)
    ordering = ("-capacity", "name", "pk")
    readonly_fields = ("id", "large_location")
    prepopulated_fields = {"slug": ("name",)}
    fields = ("id", "name", "address", "capacity", "slug", "large_location")
    inlines = (ShootingInline,)

    @admin.display(description="Большая локация", boolean=True)
    def large_location(self, obj):
        return obj.is_large if obj.pk else None


admin.site.site_header = "КиноПлан — управление съёмками"
admin.site.site_title = "КиноПлан"
admin.site.index_title = "Фильмы, локации и график съёмок"
