from django.db import migrations, models
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    # Таблица транслитерации зафиксирована в миграции, не зависит от live-модели.
    cyrillic = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    latin = (
        "a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l",
        "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh", "ts", "ch",
        "sh", "shch", "", "y", "", "e", "yu", "ya",
    )
    translation = str.maketrans(dict(zip(cyrillic, latin)))
    Location = apps.get_model("locations", "Location")
    for location in Location.objects.using(schema_editor.connection.alias).all():
        base = slugify(location.name.lower().translate(translation))[:170]
        location.slug = f"{base or 'location'}-{location.pk}"
        location.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("locations", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="location", name="slug",
            field=models.SlugField(
                "Адрес страницы", max_length=200, blank=True, null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="location", name="is_large",
            field=models.GeneratedField(
                expression=models.Case(
                    models.When(capacity__gte=50, then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                ),
                output_field=models.BooleanField(), db_persist=True,
                verbose_name="Большая локация",
            ),
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="location", name="slug",
            field=models.SlugField(
                "Адрес страницы", max_length=200, blank=True, unique=True,
            ),
        ),
    ]
