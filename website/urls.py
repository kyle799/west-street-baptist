from django.urls import path

from . import health, views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("visit/", views.visit, name="visit"),
    path("contact/", views.contact, name="contact"),
    path("prayer/", views.prayer, name="prayer"),
    path("healthz", health.healthz, name="healthz"),
]
