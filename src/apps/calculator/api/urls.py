from django.urls import path

from apps.calculator.api import views

urlpatterns = [
    path("cities/", views.cities_list, name="api-cities-list"),
    path("routes/", views.routes_list, name="api-routes-list"),
    path("calculate/", views.calculate, name="api-calculate"),
]
