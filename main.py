from datetime import date

# Данные одной сцены/съёмки (пока без коллекций — просто переменные)
film_title = "Полночный экспресс"
scene_number = 12
location_name = "Вокзал, павильон 3"
shooting_date = date(2026, 10, 5)
is_location_busy = False  # занятость локации на эту дату

def check_location_availability(is_busy):
    if is_busy:
        return "Локация занята на выбранную дату"
    return "Локация свободна для съёмки"

def get_days_until_shooting(shoot_date):
    today = date(2026, 9, 14)
    delta = today - shoot_date
    return delta.days

def get_shooting_status(days_left):
    if days_left < 0:
        return "Съёмка уже прошла"
    elif days_left == 0:
        return "Съёмка сегодня"
    else:
        return f"До съёмки осталось {days_left} дн."

print(f"Фильм: {film_title}")
print(f"Сцена №{scene_number}")
print(f"Локация: {location_name}")
print(f"Дата съёмки: {shooting_date}")
print(check_location_availability(is_location_busy))

days = get_days_until_shooting(shooting_date)
print(get_shooting_status(days))