# basic URL Configurations
from django.urls import include, path

# import everything from views
from . import views

# specify URL Path for rest_framework
urlpatterns = [
    path("save-nsd-articles", views.save_nsd_articles, name="routes"),
]
