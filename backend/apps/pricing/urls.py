# backend/apps/pricing/urls.py

from django.urls import path
from apps.pricing import views

urlpatterns = [
    path("quote/", views.estimate_quote, name="estimate-quote"),
    path("addons/", views.list_addons, name="list-addons"),
    path("house-sizes/", views.list_house_sizes, name="list-house-sizes"),
]