from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="clubIndex"),
    path("club/<str:clubID>", views.clubPage, name="clubDetails")
]