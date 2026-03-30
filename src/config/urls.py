from django.contrib import admin
from django.urls import include, path

from apps.calculator.views import calculator_index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", calculator_index, name="home"),
    path("calculator/", include("apps.calculator.urls")),
]
