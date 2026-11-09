"""Правила ORM и составные сценарии ПР9."""
from datetime import date
from io import StringIO

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import Client

from db import queries
from films.models import Film, Scene
from locations.models import Location
from shootings.models import Shooting
from shootings.services import (
    cancel_shooting, delete_cancelled_shooting, reschedule_shooting,
    schedule_shooting,
)


def test_links_and_reverse_relations():
    shooting = Shooting.objects.select_related(
        "scene__film", "location",
    ).get(pk=1)
    assert shooting in shooting.scene.shootings.all()
    assert shooting.scene in shooting.scene.film.scenes.all()
    with pytest.raises(ProtectedError):
        shooting.location.delete()


def test_crud_and_capacity_validation():
    scene = Scene.objects.get(film_id=1, number=1)
    location = Location.objects.get(pk=1)
    shooting = schedule_shooting(
        scene=scene, location=location, shooting_date=date(2030, 1, 1),
    )
    reschedule_shooting(shooting, date(2030, 1, 2))
    shooting.refresh_from_db()
    assert shooting.shooting_date == date(2030, 1, 2)
    with pytest.raises(ValueError):
        delete_cancelled_shooting(shooting)
    cancel_shooting(shooting)
    delete_cancelled_shooting(shooting)
    assert not Shooting.objects.filter(shooting_date__year=2030).exists()
    with pytest.raises(ValidationError, match="не вмещает"):
        schedule_shooting(
            scene=scene, location=Location.objects.get(pk=3),
            shooting_date=date(2030, 1, 3),
        )


def test_uniqueness_enforced_by_database():
    original = Shooting.objects.active().first()
    with pytest.raises(IntegrityError), transaction.atomic():
        Shooting.objects.create(
            scene=original.scene, location=original.location,
            shooting_date=original.shooting_date,
        )


def test_positive_capacity_enforced():
    with pytest.raises(IntegrityError), transaction.atomic():
        Location.objects.create(name="Некорректная", capacity=0)


def test_scene_number_unique_in_film():
    scene = Scene.objects.first()
    with pytest.raises(IntegrityError), transaction.atomic():
        Scene.objects.create(
            film=scene.film, number=scene.number,
            description="Дубликат", crew_size=1,
        )


def test_import_refuses_nonempty_destination(test_db_path):
    with pytest.raises(CommandError, match="уже содержат"):
        call_command("import_legacy", source=test_db_path)
    assert Shooting.objects.count() == 7


def test_orm_demo_rolls_back():
    call_command("orm_demo", stdout=StringIO())
    assert Film.objects.count() == 2
    assert Location.objects.get(pk=1).capacity == 40


def test_related_list_uses_one_query(django_assert_num_queries):
    with django_assert_num_queries(1):
        labels = [(s.film_title, s.location_name)
                  for s in queries.get_shootings()]
    assert len(labels) == 7


def test_search_across_fields():
    assert queries.get_films("Полночный").count() == 1
    assert queries.get_locations(search="Каланчёвская").count() == 1
    assert queries.get_locations(search="Вокзал").count() == 1


def test_filters_sort_and_pagination_together():
    Shooting.objects.bulk_create([
        Shooting(scene_id=1, location_id=1, shooting_date=date(2030, 1, day))
        for day in (1, 2)
    ])
    response = Client().get("/shootings/?status=active&sort=-date")
    assert response.status_code == 200
    assert response.context["page_obj"].paginator.count == 6
    assert len(response.context["shootings"]) == 5
    assert ("status=active&amp;sort=-date&amp;page=2"
            in response.content.decode())
    second = Client().get("/shootings/?status=active&sort=-date&page=2")
    assert len(second.context["shootings"]) == 1
    dates = [s.shooting_date for s in response.context["shootings"]]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.parametrize("params", [
    "film=abc", "location=-1", "date=invalid", "sort=bad", "status=bad",
    "page=abc", "page=999999999999999999999", "q=несуществующий",
])
def test_invalid_and_empty_selections(params):
    assert Client().get("/shootings/?" + params).status_code == 200


def test_filtered_film_search():
    response = Client().get("/shootings/?q=Арбате&film=1&location=3")
    assert all(s.film_id == 1 and s.location_id == 3
               for s in response.context["shootings"])
    assert response.context["page_obj"].paginator.count == 2


def test_failed_import_rolls_back_all_rows(tmp_path, test_db_path):
    import shutil
    import sqlite3
    Shooting.objects.all().delete()
    Scene.objects.all().delete()
    Film.objects.all().delete()
    Location.objects.all().delete()
    source = tmp_path / "broken.sqlite"
    shutil.copy(test_db_path, source)
    conn = sqlite3.connect(source)
    conn.execute("PRAGMA ignore_check_constraints=ON")
    conn.execute("UPDATE scenes SET crew_size=0 WHERE id=1")
    conn.commit()
    conn.close()
    with pytest.raises(IntegrityError):
        call_command("import_legacy", source=source)
    assert Film.objects.count() == 0
    assert Scene.objects.count() == 0
    assert Location.objects.count() == 0
