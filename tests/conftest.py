"""Настройка Django для тестов веб-страниц."""
import os

import django
from django.test.utils import setup_test_environment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kinoplan.settings")
django.setup()
setup_test_environment()
