from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="eventIndex"),
    path("details/", views.allEvents, name="eventsDetails"),
    path("event/<str:eventID>/<str:subEventID>/<str:sessionID>/", views.eventSummary, name="eventSummary"),
    path("event/<str:eventID>/<str:subEventID>/<str:sessionID>/add/", views.adminAdd, name="eventAddPage"),
]