from django.urls import include, path

from apps.calculator.views import calculator_index

urlpatterns = [
    path("", calculator_index, name="calculator-index"),
    path("api/", include("apps.calculator.api.urls")),
]
