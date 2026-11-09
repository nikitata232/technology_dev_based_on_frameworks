"""ASCII-транслитерация названий локаций для постоянных адресов."""
from django.utils.text import slugify

CYRILLIC = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
LATIN = (
    "a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l",
    "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh", "ts", "ch",
    "sh", "shch", "", "y", "", "e", "yu", "ya",
)


def location_slug(name):
    return slugify(name.lower().translate(str.maketrans(
        dict(zip(CYRILLIC, LATIN)),
    )))[:170] or "location"
