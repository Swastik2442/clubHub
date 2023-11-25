from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import render

from schedule.utils import check_calendar_permissions
from schedule.views import _api_occurrences
from schedule.models import Event as schedulerEvent, Calendar, Rule

from dotenv import load_dotenv

from clubHub.settings import TIME_ZONE
from base.views import isAdminMember
from .models import Event, EventCoreTeam, EventOperationsTeam, EventSession, SubEvent
from base.utils import createCalendar

from datetime import datetime
import logging, os, json

load_dotenv()
logger = logging.getLogger(__name__)
calendarName = os.getenv('CALENDAR_NAME')
calendarDescription = os.getenv('CALENDAR_DESCRIPTION')
minimumDate = os.getenv('MIN_DATE')
maximumDate = os.getenv('MAX_DATE')

def serialize_datetime(obj): 
    if isinstance(obj, datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 

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

    events = json.dumps(events, default=serialize_datetime)
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

def eventSummary(request: HttpRequest, eventID: str, subEventID: str, sessionID: str):
    """A Django View for viewing the Summary of an Event."""
    try:
        event = Event.objects.get(id__exact=eventID)
        subEvents = None
        sessions = None
        coreTeam = None
        operationsTeams = None
        if subEventID == '0' and sessionID == '0':
            subEvents = SubEvent.objects.filter(eventID__exact=eventID).order_by("startDate", "endDate")
            sessions = EventSession.objects.filter(eventID__exact=eventID).order_by("startDate", "endDate")
            coreTeam = EventCoreTeam.objects.filter(eventID__exact=eventID)
            operationsTeams = EventOperationsTeam.objects.filter(eventID__exact=eventID)
        elif sessionID == '0':
            event = SubEvent.objects.get(eventID__exact=eventID, subEventID__exact=subEventID)
        else:
            event = EventSession.objects.get(eventID__exact=eventID, sessionID__exact=sessionID)
        context = {
            'event': event, 'subEvents': subEvents, 'sessions': sessions,
            'coreTeam': coreTeam, 'operationsTeams': operationsTeams,
            'adminUser': isAdminMember(request.user)
        }
        return render(request, "eventCal/event.html", context)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No such Event, Sub-Event or Session")