from django.db import migrations, models
from django.utils import timezone


def forwards(apps, schema_editor):
    Shooting = apps.get_model("shootings", "Shooting")
    rows = Shooting.objects.using(schema_editor.connection.alias)
    rows.filter(is_cancelled=True).update(status="cancelled")
    rows.filter(
        is_cancelled=False, shooting_date__lt=timezone.localdate(),
    ).update(status="completed")


def backwards(apps, schema_editor):
    Shooting = apps.get_model("shootings", "Shooting")
    Shooting.objects.using(schema_editor.connection.alias).filter(
        status="cancelled",
    ).update(is_cancelled=True)


class Migration(migrations.Migration):
    dependencies = [("shootings", "0001_initial")]
    operations = [
        migrations.RemoveConstraint(
            model_name="shooting", name="unique_active_location_date",
        ),
        migrations.AddField(
            model_name="shooting", name="status",
            field=models.CharField(
                "Статус", max_length=12, default="active",
                choices=[("active", "Активна"), ("cancelled", "Отменена"),
                         ("completed", "Завершена")],
            ),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(model_name="shooting", name="is_cancelled"),
        migrations.AddConstraint(
            model_name="shooting",
            constraint=models.CheckConstraint(
                condition=models.Q(status__in=["active", "cancelled", "completed"]),
                name="valid_shooting_status",
            ),
        ),
        migrations.AddConstraint(
            model_name="shooting",
            constraint=models.UniqueConstraint(
                fields=("location", "shooting_date"),
                condition=models.Q(status="active"),
                name="unique_active_location_date",
                violation_error_message="Локация уже занята на эту дату.",
            ),
        ),
    ]
