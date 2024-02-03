from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:clan_name>/", views.testing_page, name="testing_page"),
]