from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpRequest, Http404
from dotenv import load_dotenv
import requests
import logging, os

load_dotenv()

SIGNUP_WEBHOOK = os.getenv("SIGNUP_WEBHOOK")

logger = logging.getLogger(__name__)

def isAdminMember(user):
    """Checks if Logged In User is a Club Admin."""
    return user.groups.filter(name='clubAdmin').exists()

def index(request):
    """The Django View for the Website Index Page."""
    return render(request, "base/index.html")

@user_passes_test(isAdminMember, login_url='/login')
def admin_view(request: HttpRequest):
    """The Django View for the Club Admin Page."""
    return render(request, "base/admin.html")

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
            return render(request, 'login.html', {'error': 'Invalid username or password'})
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
                return render(request, 'signup.html', {'submitted': True, 'error': True})
            else:
                logger.info(f"Payload for new Sign-Up delivered with code {result.status_code}")
                return render(request, 'base/signup.html', {'submitted': True, 'error': False})
        else:
            return render(request, 'base/signup.html', {'submitted': True, 'error': True})
    else:
        return render(request, 'base/signup.html')