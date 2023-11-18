from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from schedule.utils import check_calendar_permissions
from schedule.views import _api_occurrences
from schedule.models import Event as schedulerEvent, Calendar

from dotenv import load_dotenv

from clubHub.settings import TIME_ZONE
from base.views import isAdminMember
from .models import Event, SubEvent
from .utils import createCalendar

import logging, os

load_dotenv()
logger = logging.getLogger(__name__)
calendarName = os.getenv('CALENDAR_NAME')
calendarDescription = os.getenv('CALENDAR_DESCRIPTION')
minimumDate = os.getenv('MIN_DATE')
maximumDate = os.getenv('MAX_DATE')

@check_calendar_permissions
def index(request: HttpRequest):
    """A Django View for Viewing the Event Calendar."""
    start = request.GET.get("start", minimumDate)
    end = request.GET.get("end", maximumDate)

    events: list
    try:
        events = _api_occurrences(start, end, calendarName, TIME_ZONE)
    except ObjectDoesNotExist:
        createCalendar(calendarName, calendarDescription)
        events = _api_occurrences(start, end, calendarName, TIME_ZONE)

    return render(request, "eventCal/index.html", {'events': events})

def allEvents(request: HttpRequest):
    """A Django View for viewing the Details of all Events."""
    events = None
    search = request.GET.get('search', '')
    if search == '':
        events = Event.objects.all().order_by("-startDate", "-endDate")
    else:
        events = Event.objects.filter(name__contains=search).order_by("-startDate", "-endDate")
    page = request.GET.get('page', 1)
    paginator = Paginator(events, 10)
    try:
        details = paginator.page(page)
    except PageNotAnInteger:
        details = paginator.page(1)
    except EmptyPage:
        details = paginator.page(paginator.num_pages)
    return render(request, "eventCal/events.html", {"details": details, 'search': search})
# TODO: Remake events.html if possible

def eventSummary(request: HttpRequest, eventID: str, subEventID: str):
    """A Django View for viewing the Summary of an Event."""
    try:
        event = Event.objects.get(id__exact=eventID)
        subEvents = None
        if subEventID != '0':
            event = SubEvent.objects.get(eventID__exact=eventID, subEventID__exact=subEventID)
        else:
            subEvents = SubEvent.objects.filter(eventID__exact=eventID).order_by("-startDate", "-endDate")
        return render(request, "eventCal/event.html", {'event': event, 'subEvents': subEvents})
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No such Event or Sub-Event")

@user_passes_test(isAdminMember)
def adminAdd(request: HttpRequest, eventID: str, subEventID: str):
    """A Django View for Adding Events to Event Calendar."""
    submitted = False
    success = False

    try:
        event = Event.objects.get(id__exact=eventID)
        if subEventID != '0':
            event = SubEvent.objects.get(eventID__exact=eventID, subEventID__exact=subEventID)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No such Event or Sub-Event")
    
    if request.method == "POST":
        submitted = True
        data = {
            'title': event.name,
            'start': event.startDate,
            'end': event.endDate,
            'creator': request.user,
            'calendar': Calendar.objects.get(slug=calendarName)
        }
        try:
            sEvent = schedulerEvent(**data)
            sEvent.save()
            success = True
        except Exception as err:
            logger.warning(err)

    return render(request, "eventCal/adminAdd.html", {'event': event, 'submitted': submitted, 'success': success})

@user_passes_test(isAdminMember)
def adminEdit(request: HttpRequest, eventID: str, subEventID: str):
    """A Django View for Editing Events."""
    return render(request, "eventCal/adminEdit.html")