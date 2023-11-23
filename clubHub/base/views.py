from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpRequest, Http404
from django.db import connection
from dotenv import load_dotenv
import requests

import logging, os

from cHub.models import *
from eventCal.models import *

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

load_dotenv()
SIGNUP_WEBHOOK = os.getenv("SIGNUP_WEBHOOK")
logger = logging.getLogger(__name__)

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

@user_passes_test(isAdminMember, login_url='/login')
def adminDash(request: HttpRequest):
    """The Django View for the Admin Panel."""
    return render(request, "base/adminDash.html", {'tables': tables})

@user_passes_test(isAdminMember, login_url='/login')
def adminAdd(request: HttpRequest, opt: int):
    """The Django View for Adding Data in the Database."""
    context = {"optionNo": opt, 'option': options[opt], 'tables': tables}
    if request.method == 'POST':
        if opt == 1:
            print()
    else:
        if opt == 2:
            branches = Branch.objects.all().order_by(*options[2][2])
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
    option = options.get(opt, None)
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