from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

urlpatterns = [
    path("apis/", include("apis.urls")),
]
