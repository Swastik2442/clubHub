from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="eventIndex"),
    path("details/", views.allEvents, name="eventsDetails"),
    path("event/<str:eventID>/<str:subEventID>/", views.eventSummary, name="eventSummary"),
    path("event/<str:eventID>/<str:subEventID>/add/", views.adminAdd, name="eventAddPage"),
    path("event/<str:eventID>/<str:subEventID>/edit/", views.adminEdit, name="eventEditPage"),
]