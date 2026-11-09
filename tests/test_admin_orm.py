"""Админка, статусы, миграции и расширения ПР10."""
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.test import Client
from django.urls import reverse

from db import queries
from locations.models import Location
from shootings.models import Shooting


@pytest.fixture
def admin_client():
    user = get_user_model().objects.create_superuser(
        "test_admin", "admin@example.test", "Local-test-pass-2026!",
    )
    client = Client()
    client.force_login(user)
    return client


@pytest.mark.parametrize("url", [
    "/admin/", "/admin/films/film/", "/admin/films/scene/",
    "/admin/locations/location/", "/admin/shootings/shooting/",
    "/admin/locations/location/1/change/", "/admin/films/film/1/change/",
    "/admin/shootings/shooting/1/change/", "/admin/shootings/shooting/add/",
])
def test_admin_pages(admin_client, url):
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "КиноПлан" in response.content.decode()


def test_admin_requires_login():
    assert Client().get("/admin/shootings/shooting/").status_code == 302


def test_admin_search_and_filter(admin_client):
    response = admin_client.get(
        "/admin/shootings/shooting/?q=Северное&status__exact=active",
    )
    rows = response.context["cl"].queryset
    assert rows.count() == 3
    assert all(s.status == "active" and s.film_id == 2 for s in rows)


def test_admin_action_updates_public_pages(admin_client):
    response = admin_client.post("/admin/shootings/shooting/", {
        "action": "mark_cancelled", "_selected_action": [3],
    })
    assert response.status_code == 302
    assert not queries.is_location_busy(1, date(2026, 11, 10))
    assert Shooting.objects.get(pk=3).status == Shooting.Status.CANCELLED


def test_conflicting_admin_action_rolls_back(admin_client):
    duplicate = Shooting.objects.create(
        scene_id=1, location_id=1, shooting_date=date(2026, 11, 10),
        status=Shooting.Status.CANCELLED,
    )
    response = admin_client.post("/admin/shootings/shooting/", {
        "action": "mark_active", "_selected_action": [duplicate.pk],
    }, follow=True)
    assert "Изменения отменены" in response.content.decode()
    duplicate.refresh_from_db()
    assert duplicate.status == Shooting.Status.CANCELLED


@pytest.mark.parametrize("status,busy", [
    (Shooting.Status.ACTIVE, True), (Shooting.Status.CANCELLED, False),
    (Shooting.Status.COMPLETED, False),
])
def test_availability_respects_all_statuses(status, busy):
    Shooting.objects.filter(pk=3).update(status=status)
    assert queries.is_location_busy(1, date(2026, 11, 10)) == busy
    free = Location.objects.available_on(date(2026, 11, 10))
    assert free.filter(pk=1).exists() != busy


def test_generated_field_recomputes_and_slug_stays_stable():
    location = Location.objects.get(pk=1)
    old_slug = location.slug
    assert not location.is_large
    location.capacity = 60
    location.name = "Новое имя"
    location.save()
    location.refresh_from_db()
    assert location.is_large
    assert location.slug == old_slug
    assert location.slug.isascii()
    assert Client().get(location.get_absolute_url()).status_code == 200
    assert Client().get("/locations/1/").status_code == 200


def test_new_cyrillic_slugs_are_unique():
    first = Location.objects.create(name="Новая площадка", capacity=60)
    second = Location.objects.create(name="Новая площадка", capacity=30)
    assert first.slug.startswith("novaya-ploshchadka-")
    assert first.slug != second.slug
    assert reverse("locations:detail_slug", args=[first.slug])


def test_statistics_counts_all_statuses():
    totals = queries.get_shooting_totals()
    assert tuple(totals[k] for k in (
        "active", "cancelled", "completed",
    )) == (4, 1, 2)
    assert totals["total"] == sum(totals[key] for key in (
        "active", "cancelled", "completed",
    ))
    assert "завершённых" in Client().get(
        "/shootings/statistics/",
    ).content.decode()


def test_manager_methods_and_f_annotation(django_assert_num_queries):
    assert Shooting.objects.cancelled().count() == 1
    assert Shooting.objects.completed().count() == 2
    with django_assert_num_queries(1):
        rows = list(Shooting.objects.active().on_date(
            date(2026, 11, 10),
        ).with_related().with_capacity_margin())
        assert all(row.capacity_margin >= 0 for row in rows)
        assert all(row.scene.film.title and row.location.name for row in rows)


def test_invalid_status_rejected_by_database():
    with pytest.raises(IntegrityError), transaction.atomic():
        Shooting.objects.filter(pk=1).update(status="unknown")


def test_context_processor_on_multiple_pages():
    for url in ("/", "/films/", "/locations/"):
        response = Client().get(url)
        assert response.context["site_name"] == "КиноПлан"
        assert response.context["site_locations_count"] == 4


def test_detail_and_list_have_no_n_plus_one(django_assert_num_queries):
    # Detail: one JOIN plus one query for the common footer.
    with django_assert_num_queries(2):
        assert Client().get("/shootings/3/").status_code == 200
    # List: count, locations, films, paginated JOIN, common footer.
    with django_assert_num_queries(5):
        assert Client().get("/shootings/").status_code == 200


@pytest.mark.django_db(transaction=True)
def test_status_data_migration():
    executor = MigrationExecutor(connection)
    latest = executor.loader.graph.leaf_nodes()
    executor.migrate([("shootings", "0001_initial")])
    old = executor.loader.project_state([("shootings", "0001_initial")]).apps
    LegacyShooting = old.get_model("shootings", "Shooting")
    try:
        LegacyShooting.objects.filter(pk=2).update(is_cancelled=True)
        LegacyShooting.objects.filter(pk=1).update(
            is_cancelled=False, shooting_date=date(2026, 10, 20),
        )
        executor = MigrationExecutor(connection)
        executor.migrate(latest)
        assert Shooting.objects.get(pk=2).status == Shooting.Status.CANCELLED
        assert Shooting.objects.get(pk=1).status == Shooting.Status.COMPLETED
        assert Shooting.objects.get(pk=3).status == Shooting.Status.ACTIVE
    finally:
        MigrationExecutor(connection).migrate(latest)


def test_inline_edit_updates_related_shooting(admin_client):
    location = Location.objects.get(pk=1)
    rows = list(location.shootings.order_by("pk"))
    data = {
        "name": location.name, "address": location.address,
        "capacity": location.capacity, "slug": location.slug,
        "shootings-TOTAL_FORMS": len(rows),
        "shootings-INITIAL_FORMS": len(rows),
        "shootings-MIN_NUM_FORMS": 0, "shootings-MAX_NUM_FORMS": 1000,
        "_save": "Сохранить",
    }
    for i, row in enumerate(rows):
        data.update({
            f"shootings-{i}-id": row.pk,
            f"shootings-{i}-location": location.pk,
            f"shootings-{i}-scene": row.scene_id,
            f"shootings-{i}-shooting_date": row.shooting_date.isoformat(),
            f"shootings-{i}-status": (
                "cancelled" if row.pk == 3 else row.status
            ),
        })
    response = admin_client.post(
        "/admin/locations/location/1/change/", data,
    )
    assert response.status_code == 302
    assert Shooting.objects.get(pk=3).status == Shooting.Status.CANCELLED
    assert not queries.is_location_busy(1, date(2026, 11, 10))
