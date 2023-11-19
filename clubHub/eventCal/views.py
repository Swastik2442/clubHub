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
from .models import Event, SubEvent, EventSession
from .utils import createCalendar

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
        if subEventID == '0' and sessionID == '0':
            subEvents = SubEvent.objects.filter(eventID__exact=eventID).order_by("startDate", "endDate")
            sessions = EventSession.objects.filter(eventID__exact=eventID).order_by("startDate", "endDate")
        elif sessionID == '0':
            event = SubEvent.objects.get(eventID__exact=eventID, subEventID__exact=subEventID)
        else:
            event = EventSession.objects.get(eventID__exact=eventID, sessionID__exact=sessionID)
        return render(request, "eventCal/event.html", {'event': event, 'subEvents': subEvents, 'sessions': sessions, 'adminUser': isAdminMember(request.user)})
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No such Event, Sub-Event or Session")

@user_passes_test(isAdminMember, login_url='/login')
def adminAdd(request: HttpRequest, eventID: str, subEventID: str, sessionID: str):
    """A Django View for Adding Events to Event Calendar."""
    try:
        event = Event.objects.get(id__exact=eventID)
        if subEventID != '0':
            event = SubEvent.objects.get(eventID__exact=eventID, subEventID__exact=subEventID)
        if sessionID != '0':
            event = EventSession.objects.get(eventID__exact=eventID, sessionID__exact=sessionID)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No such Event, Sub-Event or Session")
    
    success = False
    alreadyAdded = False

    eventName = None
    repetitionRule = None
    if isinstance(event, Event):
        eventName = event.name
        try:
            repetitionRule = Rule.objects.get(frequency=event.repetition)
        except ObjectDoesNotExist:
            pass
    elif isinstance(event, SubEvent):
        eventName = event.name + " - " + event.eventID.name
    else:
        eventName = event.sessionName + " - " + event.eventID.name
    endDate = event.endDate
    if endDate == None:
        endDate = event.startDate.replace(hour=23, minute=59, second=59)

    data = {
        'title': eventName,
        'start': event.startDate,
        'end': endDate,
        'creator': request.user,
        'rule': repetitionRule,
        'calendar': Calendar.objects.get(slug=calendarName)
    }
    try:
        check = schedulerEvent.objects.get(title=data['title'], start=data['start'], end=data['end'])
        alreadyAdded = True
    except ObjectDoesNotExist:
        pass
    
    if not alreadyAdded:
        try:
            sEvent = schedulerEvent(**data)
            sEvent.save()
            success = True
        except Exception as err:
            logger.warning(err)

    return render(request, "eventCal/adminAdd.html", {'event': event, 'success': success, 'alreadyAdded': alreadyAdded})