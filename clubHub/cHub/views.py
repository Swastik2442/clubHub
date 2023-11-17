from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from datetime import datetime

from .models import *

def index(request: HttpResponse):
    """A Django View for the Index Page of the Club Hub."""
    currentYear = datetime.now().year
    clubs = Club.objects.filter(club_year__exact=currentYear)
    if not clubs:
        clubs = Club.objects.filter(club_year__exact=currentYear-1)
    return render(request, "cHub/index.html", {'clubs': clubs})

def clubPage(request: HttpResponse, clubID: str):
    """A Django View for the Club Details Page."""
    clubs = Club.objects.filter(club_id__exact=clubID).order_by('-club_year')
    if not clubs:
        return HttpResponseNotFound(request)
    
    currentYear = datetime.now().year
    requestedYear = int(request.GET.get('year', currentYear))
    clubYears = list()
    for i in clubs:
        clubYears.append(i.club_year)
    try:
        club = clubs[clubYears.index(requestedYear)]
    except ValueError:
        club = clubs[0]

    presidentName = Student.objects.get(id__exact=club.president_id.id).name
    vicePresidentName = Student.objects.get(id__exact=club.vice_president_id.id).name
    clubHeads = [presidentName, vicePresidentName]

    clubMembers = ClubMember.objects.filter(club_id__exact=club).order_by('role')
    memberDetails = list()
    for i in clubMembers:
        memberName = Student.objects.get(id__exact=i.member.id).name
        memberDetails.append([memberName, i.role])

    return render(request, "cHub/club.html", {'club': club, 'clubYears': clubYears, 'clubHeads': clubHeads, 'clubMembers': memberDetails})