# basic URL Configurations
from django.urls import path

# import everything from views
from . import views

# specify URL Path for rest_framework
urlpatterns = [
    path("save-nsd-articles", views.save_nsd_articles, name="routes"),
    path(
        "save-samprativartah-articles",
        views.save_samprati_news_articles,
        name="routes"
    ),
    path(
        "save-samprativartah-lit-articles",
        views.save_samprati_lit_articles,
        name="routes",
    ),
    path(
        "save-sanskritvarta-articles",
        views.save_sanskritvarta_articles,
        name="routes",
    ),
]
