"""Администрирование съёмок и безопасные массовые переходы статусов."""
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from .models import Shooting


class ShootingInline(admin.TabularInline):
    model = Shooting
    extra = 0
    fields = ("scene", "shooting_date", "status")
    show_change_link = True

    def get_queryset(self, request):
        return super().get_queryset(request).with_related()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "scene":
            from films.models import Scene
            kwargs["queryset"] = Scene.objects.select_related("film")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Shooting)
class ShootingAdmin(admin.ModelAdmin):
    list_display = ("id", "shooting_date", "film_title", "scene_number",
                    "location", "status", "capacity_margin")
    list_filter = ("status", "shooting_date", "location", "scene__film")
    search_fields = (
        "scene__film__title", "scene__description", "location__name",
    )
    list_select_related = ("scene__film", "location")
    ordering = ("-shooting_date", "pk")
    date_hierarchy = "shooting_date"
    readonly_fields = ("id", "capacity_margin")
    fields = ("id", "scene", "location", "shooting_date", "status",
              "capacity_margin")
    autocomplete_fields = ("scene", "location")
    actions = ("mark_cancelled", "mark_completed", "mark_active")
    list_per_page = 20
    empty_value_display = "—"

    def get_queryset(self, request):
        return (super().get_queryset(request)
                .with_related().with_capacity_margin())

    @admin.display(description="Фильм", ordering="scene__film__title")
    def film_title(self, obj):
        return obj.film_title

    @admin.display(description="Сцена", ordering="scene__number")
    def scene_number(self, obj):
        return obj.scene.number

    @admin.display(description="Свободных мест")
    def capacity_margin(self, obj):
        if not obj.pk:
            return "—"
        return obj.location.capacity - obj.scene.crew_size

    def set_status(self, request, queryset, status):
        try:
            with transaction.atomic():
                count = 0
                for shooting in queryset.select_for_update().with_related():
                    shooting.status = status
                    shooting.full_clean()
                    shooting.save(update_fields=["status"])
                    count += 1
        except (ValidationError, IntegrityError) as error:
            self.message_user(
                request, f"Изменения отменены: {error}", level=messages.ERROR,
            )
        else:
            self.message_user(request, f"Обновлено съёмок: {count}.")

    @admin.action(description="Отменить выбранные съёмки")
    def mark_cancelled(self, request, queryset):
        self.set_status(request, queryset, Shooting.Status.CANCELLED)

    @admin.action(description="Завершить выбранные съёмки")
    def mark_completed(self, request, queryset):
        self.set_status(request, queryset, Shooting.Status.COMPLETED)

    @admin.action(description="Активировать выбранные съёмки")
    def mark_active(self, request, queryset):
        self.set_status(request, queryset, Shooting.Status.ACTIVE)
