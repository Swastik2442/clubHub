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

@user_passes_test(isAdminMember, login_url='/login')
def admin_view(request: HttpRequest):
    """The Django View for the Club Admin Page."""
    return render(request, "base/admin.html", {"options": options})

# TODO: Add Order By Query
options = {
    1: ["Review Branches", "Check the Available Branches in the University", Branch],
    2: ["Review Students", "Check the Data of Students available in the Database", Student],
    3: ["Review Clubs", "Check the Clubs available in the Database", Club],
    4: ["Review Club Members", "Check the Members of Clubs available in the Database", ClubMember],
    5: ["Review Events", "Check the Events available in the Database", Event],
    6: ["Review Sessions", "Check the Event Sessions available in the Database", EventSession],
    7: ["Review Core Teams", "Check the Core Teams' details available in the Database", EventCoreTeam],
    8: ["Review Operations Teams", "Check the Operations Teams' details available in the Database", EventOperationsTeam],
    9: ["Review Operations Teams' Members", "Check the Members of Operations Teams available in the Database", EventOperationMember],
    10: ["Review Sub-Events", "Check the Sub-Events available in the Database", SubEvent],
    11: ["Raw SQL Queries", "Execute Raw SQL Queries in the Database", None]
}

@user_passes_test(isAdminMember, login_url='/login')
def adminOptions(request: HttpRequest, opt: int):
    """The Django View for Admin Options on the Club Admin Page."""
    option = options.get(opt, None)
    optionDetails = None
    if (opt in range(1, 11)):
        optionDetails = (option[2]).objects.all()
    elif (opt == 11):
        return rawSQL_view(request)
    else:
        return redirect("adminPage")

    page = request.GET.get('page', 1)
    paginator = Paginator(optionDetails, 10)
    try:
        details = paginator.page(page)
    except PageNotAnInteger:
        details = paginator.page(1)
    except EmptyPage:
        details = paginator.page(paginator.num_pages)
    return render(request, 'base/reviewTable.html', {"optionNo": opt, "option": option, "details": details})

tables = [
    "cHub_Branch", "cHub_Student", "cHub_Club", "cHub_ClubMember",
    "eventCal_Event", "eventCal_EventSession", "eventCal_EventCoreTeam", "eventCal_EventOperationsTeam", "eventCal_EventOperationMembers", "eventCal_SubEvent"
    ]

@user_passes_test(isAdminMember, login_url='/login')
def rawSQL_view(request: HttpRequest):
    """The Django View for Processing Raw SQL on the Webpage.\nUse with Extreme Caution."""
    if (request.method == 'GET'):
        return render(request, 'base/rawSQL.html', {'tables': tables, 'output': None, 'error': False, 'errorOutput': None})
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
        return render(request, 'base/rawSQL.html', {'tables': tables, 'output': output, 'error': error, 'errorOutput': errorOutput})