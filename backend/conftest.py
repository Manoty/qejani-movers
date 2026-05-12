# backend/conftest.py
import django
from django.conf import settings

def pytest_configure():
    pass  # pytest.ini handles settings module