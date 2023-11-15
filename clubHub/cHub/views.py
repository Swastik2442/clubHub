from django.shortcuts import render
from django.http import HttpResponse
from .models import Club

from datetime import datetime

def index(request):
    currentYear = datetime.now().year
    clubs = Club.objects.filter(club_year__exact=currentYear)
    if not clubs:
        clubs = Club.objects.filter(club_year__exact=currentYear-1)
    return render(request, "cHub/index.html", {'clubs': clubs})

def clubPage(request, clubID):
    club = Club.objects.get(club_id__exact=clubID)
    return render(request, "cHub/club.html", {'club': club})