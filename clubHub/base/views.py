from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.db import connection
from dotenv import load_dotenv
from pytz import timezone
import requests

from datetime import datetime
import logging, os

from .utils import addEvent
from clubHub.settings import TIME_ZONE
from cHub.models import Branch, Student, Club, ClubMember
from eventCal.models import Event, EventSession, EventCoreTeam, EventOperationsTeam, SubEvent

load_dotenv()
SIGNUP_WEBHOOK = os.getenv("SIGNUP_WEBHOOK")
EVENT_COLOR = os.getenv("EVENT_COLOR")
SESSION_COLOR = os.getenv("SESSION_COLOR")
SUBEVENT_COLOR = os.getenv("SUBEVENT_COLOR")
logger = logging.getLogger(__name__)

tz = timezone(TIME_ZONE)
jsTimeFormat = "%Y-%m-%dT%H:%M"

tables = [
    "cHub_Branch", "cHub_Student", "cHub_Club", "cHub_ClubMember",
    "eventCal_Event", "eventCal_EventSession", "eventCal_EventCoreTeam", "eventCal_EventOperationsTeam", "eventCal_SubEvent"
    ]
options = {
    1: ["Branches", Branch, ["id"]],
    2: ["Students", Student, ["batch_no", "branch_id", "roll_no"]],
    3: ["Clubs", Club, ["-club_year", "club_id"]],
    4: ["Club Members", ClubMember, ["club_id", "role"]],
    5: ["Events", Event, ["-startDate", "-endDate", "id"]],
    6: ["Sessions", EventSession, ["eventID", "sessionID"]],
    7: ["Core Teams", EventCoreTeam, ["eventID"]],
    8: ["Operations Teams", EventOperationsTeam, ["eventID", "teamID"]],
    9: ["Sub-Events", SubEvent, ["eventID", "-startDate", "-endDate", "subEventID"]]
}
repetitionOptions = ['YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY']

def index(request):
    """The Django View for the Website Index Page."""
    return render(request, "base/index.html")

def login_view(request: HttpRequest):
    """The Django View for the Website Login Page."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next", "baseIndex"))
        else:
            return render(request, 'base/login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'base/login.html')

def signup_view(request: HttpRequest):
    """The Django View for the Website Sign-Up Page."""
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if (password1 == password2):
            ip = request.META.get('REMOTE_ADDR')
            name = request.POST.get('name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            content = f"New Sign-Up Request from {name}.\nIP Address: {ip}\nEmail: {email}\nUsername: {username}\nPassword: ||{password1}||"
            result = requests.post(SIGNUP_WEBHOOK, json={"content" : content})
            try:
                result.raise_for_status()
            except requests.exceptions.HTTPError as err:
                logger.warning(err)
                return render(request, 'base/signup.html', {'submitted': True, 'error': True})
            else:
                logger.info(f"Payload for new Sign-Up delivered with code {result.status_code}")
                return render(request, 'base/signup.html', {'submitted': True, 'error': False})
        else:
            return render(request, 'base/signup.html', {'submitted': True, 'error': True})
    else:
        return render(request, 'base/signup.html')

def logout_view(request: HttpRequest):
    """The Django View for the Website Logout Page."""
    logout(request)
    return redirect(request.GET.get("next", "baseIndex"))

def isAdminMember(user):
    """Checks if Logged In User is a Club Admin."""
    return user.groups.filter(name='clubAdmin').exists()

@user_passes_test(isAdminMember, login_url='/login')
def adminDash(request: HttpRequest):
    """The Django View for the Admin Panel."""
    return render(request, "base/adminDash.html", {'tables': tables})

@user_passes_test(isAdminMember, login_url='/login')
def adminAdd(request: HttpRequest, opt: int):
    """The Django View for Adding Data in the Database."""
    context = {"optionNo": opt, 'option': options[opt], 'tables': tables}
    if request.method == 'POST':
        submitted, error = False, True
        
        if opt == 1:
            id = request.POST.get('id', '')
            name = request.POST.get('name', '')
            submitted = True
            if not (Branch.objects.filter(id__exact=id).exists()):
                try:
                    new = Branch(id=id, name=name)
                    new.save()
                    error = False
                except Exception:
                    pass
        elif opt == 2:
            roll_no = request.POST.get('roll_no', '')
            branch_id = request.POST.get('branch_id', '')
            batch_no = request.POST.get('batch_no', '')
            name = request.POST.get('name', '')
            submitted = True
            try:
                Student.objects.get(batch_no__exact=batch_no, branch_id__exact=branch_id, roll_no__exact=roll_no)
            except Exception:
                try:
                    branch = Branch.objects.get(id__exact=branch_id)
                    new = Student(batch_no=batch_no, branch_id=branch, roll_no=roll_no, name=name)
                    new.save()
                    error = False
                except Exception:
                    pass
        elif opt == 3:
            club_id = request.POST.get('club_id', '')
            club_year = request.POST.get('club_year', '')
            club_name = request.POST.get('club_name', '')
            topic = request.POST.get('topic', '')
            faculty_mentor = request.POST.get('faculty_mentor', '')
            logo = request.POST.get('logo', '')
            faculty_mentor_picture = request.POST.get('faculty_mentor_picture', '')
            president_id = request.POST.get('president_id', '')
            vice_president_id = request.POST.get('vice_president_id', '')
            president_picture = request.POST.get('president_picture', '')
            vice_president_picture = request.POST.get('vice_president_picture', '')
            submitted = True
            if not (Club.objects.filter(club_id__exact=club_id, club_year__exact=club_year).exists()):
                try:
                    president = Student.objects.get(id__exact=president_id)
                    vicePresident = Student.objects.get(id__exact=vice_president_id)
                    new = Club(
                        club_id=club_id, club_year=club_year, club_name=club_name, topic=topic,
                        faculty_mentor=faculty_mentor, logo=logo,
                        faculty_mentor_picture=faculty_mentor_picture,
                        president_id=president, vice_president_id=vicePresident,
                        president_picture=president_picture, vice_president_picture=vice_president_picture
                    )
                    new.save()
                    error = False
                except Exception:
                    pass
        elif opt == 4:
            club_id = request.POST.get('club_id', '')
            member = request.POST.get('member', '')
            role = request.POST.get('role', '')
            submitted = True
            if not (ClubMember.objects.filter(club_id__exact=club_id, member__exact=member, role__exact=role).exists()):
                try:
                    club = Club.objects.get(id__exact=club_id)
                    member = Student.objects.get(id__exact=member)
                    new = ClubMember(club_id=club, member=member, role=role)
                    new.save()
                    error = False
                except Exception:
                    pass
        elif opt == 5:
            id = request.POST.get('id', '')
            name = request.POST.get('name', '')
            startDate = request.POST.get('startDate', '')
            endDate = request.POST.get('endDate', '')
            logo = request.POST.get('logo', '')
            location = request.POST.get('location', '')
            isOnline = request.POST.get('isOnline', '')
            organizingHead = request.POST.get('organizingHead', '')
            repetition = request.POST.get('repetition', '')
            submitted = True

            startDate = datetime.strptime(startDate, jsTimeFormat).astimezone(tz)
            if endDate != '': endDate = datetime.strptime(endDate, jsTimeFormat).astimezone(tz)
            else: endDate = None

            if organizingHead != '': organizingHead = Student.objects.get(id__exact=organizingHead)
            else: organizingHead = None

            if not (Event.objects.filter(id__exact=id).exists()):
                try:
                    new = Event(
                        id=id, name=name, startDate=startDate, endDate=endDate, logo=logo,
                        location=location, isOnline=isOnline, organizingHead=organizingHead,
                        repetition=repetition
                    )
                    new.save()
                    error = False
                    eventCreated = addEvent(name, startDate, endDate, repetition, EVENT_COLOR)
                    if (not eventCreated): error = True
                except Exception:
                    pass
        elif opt == 6:
            eventID = request.POST.get('eventID', '')
            sessionID = request.POST.get('sessionID', '')
            sessionName = request.POST.get('sessionName', '')
            startDate = request.POST.get('startDate', '')
            endDate = request.POST.get('endDate', '')
            submitted = True

            startDate = datetime.strptime(startDate, jsTimeFormat).astimezone(tz)
            if endDate != '': endDate = datetime.strptime(endDate, jsTimeFormat).astimezone(tz)
            else: endDate = None
            if not (EventSession.objects.filter(eventID__exact=eventID, sessionID__exact=sessionID).exists()):
                try:
                    event = Event.objects.get(id__exact=eventID)
                    new = EventSession(
                        eventID=event, sessionID=sessionID, sessionName=sessionName,
                        startDate=startDate, endDate=endDate
                    )
                    new.save()
                    error = False
                    name = f"{sessionName} ({event.name})"
                    eventCreated = addEvent(name, startDate, endDate, eventColour=SESSION_COLOR)
                    if (not eventCreated): error = True
                except Exception:
                    pass
        elif opt == 7:
            eventID = request.POST.get('eventID', '')
            member = request.POST.get('member', '')
            submitted = True

            event = Event.objects.get(id__exact=eventID)
            if member != '': member = Student.objects.get(id__exact=member)
            else: member = None

            if not (EventCoreTeam.objects.filter(eventID__exact=event, member__exact=member).exists()):
                try:
                    new = EventCoreTeam(eventID=event, member=member)
                    new.save()
                    error = False
                except Exception:
                    pass
        elif opt == 8:
            eventID = request.POST.get('eventID', '')
            teamID = request.POST.get('teamID', '')
            name = request.POST.get('name', '')
            coreCoordinator = request.POST.get('coreCoordinator', '')
            relatedClub = request.POST.get('relatedClub', '')
            submitted = True

            event = Event.objects.get(id__exact=eventID)
            if coreCoordinator != '': coreCoordinator = Student.objects.get(id__exact=coreCoordinator)
            else: coreCoordinator = None
            if relatedClub != '': club = Club.objects.get(id__exact=relatedClub)
            else: club = None

            if not (EventOperationsTeam.objects.filter(eventID__exact=event, teamID__exact=teamID).exists()):
                try:
                    new = EventOperationsTeam(
                        eventID=event, teamID=teamID, name=name,coreCoordinator=coreCoordinator,
                        relatedClub=club
                    )
                    new.save()
                    error = False
                except Exception:
                    pass
        elif opt == 9:
            eventID = request.POST.get('eventID', '')
            subEventID = request.POST.get('subEventID', '')
            name = request.POST.get('name', '')
            startDate = request.POST.get('startDate', '')
            endDate = request.POST.get('endDate', '')
            logo = request.POST.get('logo', '')
            location = request.POST.get('location', '')
            isOnline = request.POST.get('isOnline', '')
            coreCoordinator = request.POST.get('coreCoordinator', '')
            coordinator = request.POST.get('coordinator', '')
            submitted = True

            startDate = datetime.strptime(startDate, jsTimeFormat).astimezone(tz)
            if endDate != '': endDate = datetime.strptime(endDate, jsTimeFormat).astimezone(tz)
            else: endDate = None

            if coreCoordinator != '': coreCoordinator = Student.objects.get(id__exact=coreCoordinator)
            else: coreCoordinator = None
            if coordinator != '': coordinator = Student.objects.get(id__exact=coordinator)
            else: coordinator = None

            event = Event.objects.get(id__exact=eventID)
            if not (SubEvent.objects.filter(eventID__exact=event, subEventID__exact=subEventID).exists()):
                try:
                    new = SubEvent(
                        eventID=event, subEventID=subEventID, name=name, startDate=startDate, endDate=endDate, logo=logo,
                        location=location, isOnline=isOnline, coreCoordinator=coreCoordinator, coordinator=coordinator
                    )
                    new.save()
                    error = False
                    eventCreated = addEvent(name, startDate, endDate, eventColour=SUBEVENT_COLOR)
                    if (not eventCreated): error = True
                except Exception:
                    pass

        context['submitted'] = submitted
        context['error'] = error
    else:
        if opt == 2:
            branches = Branch.objects.all().order_by(*options[1][2])
            context['branches'] = branches
        if opt in range(3, 6) or opt in range(7, 10):
            students = Student.objects.all().order_by(*options[2][2])
            context['students'] = students
        if opt == 4 or opt == 8:
            clubs = Club.objects.all().order_by(*options[3][2])
            context['clubs'] = clubs
        if opt in range(6, 10):
            events = Event.objects.all().order_by(*options[5][2])
            context['events'] = events
    return render(request, 'base/adminAdd.html', context)

@user_passes_test(isAdminMember, login_url='/login')
def adminEdit(request: HttpRequest, opt: int):
    """The Django View for Editing Data in the Database."""
    return render(request, 'base/adminEdit.html', {'tables': tables})

@user_passes_test(isAdminMember, login_url='/login')
def adminDelete(request: HttpRequest, opt: int):
    """The Django View for Deleting Data in the Database."""
    return render(request, 'base/adminDelete.html', {'tables': tables})

@user_passes_test(isAdminMember, login_url='/login')
def adminPreview(request: HttpRequest, opt: int):
    """The Django View for Previewing Tables available in the Database."""
    option = options.get(opt, '')
    optionDetails = None
    if (opt in range(1, 10)):
        optionDetails = (option[1]).objects.all().order_by(*option[2])
    else:
        return redirect("adminDash")

    page = request.GET.get('page', 1)
    paginator = Paginator(optionDetails, 10)
    try:
        details = paginator.page(page)
    except PageNotAnInteger:
        details = paginator.page(1)
    except EmptyPage:
        details = paginator.page(paginator.num_pages)
    return render(request, 'base/previewTable.html', {"optionNo": opt, "option": option, "details": details, 'tables': tables})

@user_passes_test(isAdminMember, login_url='/login')
def rawSQL_view(request: HttpRequest):
    """The Django View for Processing Raw SQL on the Webpage.\nUse with Extreme Caution."""
    if (request.method == 'GET'):
        return render(request, 'base/rawSQL.html', {'tables': tables, 'output': None, 'error': False, 'errorOutput': None, 'tables': tables})
    else:
        output = None
        error = False
        errorOutput = None
        with connection.cursor() as cursor:
            try:
                cursor.execute(request.POST.get('query'))
                output = cursor.fetchall()
            except Exception as e:
                error = True
                errorOutput = str(e)
        try:
            if (len(output) == 0 and not error):
                output = [{'', ''}]
        except TypeError:
            pass
        return render(request, 'base/rawSQL.html', {'tables': tables, 'output': output, 'error': error, 'errorOutput': errorOutput, 'tables': tables})