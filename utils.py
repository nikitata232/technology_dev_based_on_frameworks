"""Вспомогательные функции безопасного ввода данных."""
from datetime import date, datetime
from typing import Optional

DATE_FORMAT = "%d.%m.%Y"


def input_int(prompt: str, min_value: Optional[int] = None) -> int:
    """Запросить у пользователя целое число.

    При некорректном вводе запрос повторяется.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Ошибка: введите целое число.")
            continue
        if min_value is not None and value < min_value:
            print(f"Ошибка: число должно быть не меньше {min_value}.")
            continue
        return value


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ДД.ММ.ГГГГ.

    При некорректном формате запрос повторяется.
    """
    while True:
        raw = input(prompt).strip()
        try:
            return datetime.strptime(raw, DATE_FORMAT).date()
        except ValueError:
            print("Ошибка: введите дату в формате ДД.ММ.ГГГГ.")


def input_text(prompt: str) -> str:
    """Запросить у пользователя непустую строку."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Ошибка: значение не может быть пустым.")
