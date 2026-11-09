"""Операции записи с проверкой правил предметной области."""
from django.db import transaction

from .models import Shooting


@transaction.atomic
def schedule_shooting(*, scene, location, shooting_date):
    shooting = Shooting(
        scene=scene, location=location, shooting_date=shooting_date,
    )
    shooting.full_clean()
    shooting.save()
    return shooting


@transaction.atomic
def reschedule_shooting(shooting, shooting_date):
    shooting.shooting_date = shooting_date
    shooting.full_clean()
    shooting.save(update_fields=["shooting_date"])
    return shooting


def cancel_shooting(shooting):
    shooting.status = Shooting.Status.CANCELLED
    shooting.save(update_fields=["status"])


def delete_cancelled_shooting(shooting):
    """Удаление доступно явно; обычная отмена сохраняет историю."""
    if not shooting.is_cancelled:
        raise ValueError("Удалять можно только отменённые съёмки.")
    shooting.delete()
