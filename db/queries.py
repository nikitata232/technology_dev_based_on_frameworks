"""Запросы веб-интерфейса на Django ORM (архив SQL сохранён в sql/)."""
from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.db.models.functions import TruncMonth

from films.models import Film, Scene
from locations.models import Location
from shootings.models import Shooting


def shooting_rows(queryset):
    # Один JOIN вместо отдельного запроса для каждой сцены и локации.
    return queryset.select_related("scene__film", "location")


def get_summary():
    return {
        "films_count": Film.objects.count(),
        "locations_count": Location.objects.count(),
        "active_count": Shooting.objects.filter(is_cancelled=False).count(),
    }


def get_upcoming_shootings(today, limit=3):
    return shooting_rows(Shooting.objects.filter(
        is_cancelled=False, shooting_date__gte=today,
    ))[:limit]


def get_films(search=""):
    return Film.objects.filter(title__icontains=search).annotate(
        scenes_count=Count("scenes"),
    )


def get_film(film_id):
    return Film.objects.filter(pk=film_id).first()


def get_scenes(film_id):
    return Scene.objects.filter(film_id=film_id).order_by("number")


def get_film_shootings(film_id):
    return shooting_rows(Shooting.objects.filter(scene__film_id=film_id))


def get_locations(min_capacity=0, search=""):
    return Location.objects.filter(capacity__gte=min_capacity).filter(
        Q(name__icontains=search) | Q(address__icontains=search),
    )


def get_location(location_id):
    return Location.objects.filter(pk=location_id).first()


def is_location_busy(location_id, check_date):
    return Shooting.objects.filter(
        location_id=location_id, shooting_date=check_date, is_cancelled=False,
    ).exists()


def get_location_shootings(location_id):
    return shooting_rows(Shooting.objects.filter(location_id=location_id))


def find_free_locations(check_date, crew_size):
    busy = Shooting.objects.filter(
        shooting_date=check_date, is_cancelled=False,
    ).values("location_id")
    return Location.objects.filter(capacity__gte=crew_size).exclude(
        pk__in=busy,
    ).order_by("capacity", "name", "pk")


def get_shootings():
    return shooting_rows(Shooting.objects.all())


def get_shooting(shooting_id):
    return shooting_rows(Shooting.objects.filter(pk=shooting_id)).first()


def display_date(value):
    return value.strftime("%d.%m.%Y") if value else None


def get_shooting_totals():
    totals = Shooting.objects.aggregate(
        total=Count("pk"),
        active=Count("pk", filter=Q(is_cancelled=False)),
        cancelled=Count("pk", filter=Q(is_cancelled=True)),
        first_date=Min("shooting_date"), last_date=Max("shooting_date"),
    )
    for key in ("first_date", "last_date"):
        totals[key] = display_date(totals[key])
    return totals


def get_location_statistics():
    active = Q(shootings__is_cancelled=False)
    rows = Location.objects.annotate(
        shootings_count=Count("shootings", filter=active),
        first_date=Min("shootings__shooting_date", filter=active),
        last_date=Max("shootings__shooting_date", filter=active),
    ).order_by("-shootings_count", "name").values(
        "id", "name", "capacity", "shootings_count", "first_date", "last_date",
    )
    for row in rows:
        row["first_date"] = display_date(row["first_date"])
        row["last_date"] = display_date(row["last_date"])
    return rows


def get_film_statistics():
    return Film.objects.annotate(
        scenes_count=Count("scenes"), avg_crew=Avg("scenes__crew_size"),
        max_crew=Max("scenes__crew_size"), total_crew=Sum("scenes__crew_size"),
    )


def get_busy_locations(min_count):
    return Location.objects.annotate(
        shootings_count=Count("shootings", filter=Q(
            shootings__is_cancelled=False,
        )),
    ).filter(shootings_count__gte=min_count).order_by("-shootings_count", "pk")


def get_shootings_by_month():
    rows = Shooting.objects.filter(is_cancelled=False).order_by().annotate(
        month=TruncMonth("shooting_date"),
    ).values("month").annotate(shootings_count=Count("pk")).order_by("month")
    return [{**row, "month": row["month"].strftime("%m.%Y")} for row in rows]


def get_unscheduled_scenes():
    planned = Shooting.objects.filter(is_cancelled=False).values("scene_id")
    return Scene.objects.exclude(pk__in=planned).values(
        "film_id", "description", "crew_size",
        film_title=F("film__title"), scene_number=F("number"),
    ).order_by("film__title", "number")
