from django.db import models
from cHub.models import Student

class Event(models.Model):
    """A Django Model representing an Event."""
    id = models.CharField(primary_key=True, max_length=4)
    startDate = models.DateTimeField(blank=False)
    endDate = models.DateTimeField(blank=True)
    logo = models.URLField(blank=True)
    location = models.CharField(blank=True, max_length=50)
    isOnline = models.BooleanField(blank=False)
    organizingHead = models.ForeignKey(Student, models.RESTRICT, blank=True)

class EventSession(models.Model):
    """A Django Model representing the Sessions of Events."""
    eventID = models.ForeignKey(Event, models.RESTRICT, blank=False)
    sessionID = models.CharField(max_length=4, blank=False)
    sessionName = models.CharField(max_length=20, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='session_primary_key_constraint',
                fields=['eventID', 'sessionID']
            )
        ]

class EventCoreTeam(models.Model):
    """A Django Model representing the Core Team Members of an Event (if any)."""
    eventID = models.ForeignKey(Event, models.RESTRICT, blank=False)
    member = models.ForeignKey(Student, models.RESTRICT, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='coreTeam_primary_key_constraint',
                fields=['eventID', 'member']
            )
        ]

class SubEvent(models.Model):
    """A Django Model representing the Sub-Events in an Event (if any)."""
    eventID = models.ForeignKey(Event, models.RESTRICT, blank=False)
    subEventID = models.CharField(max_length=4, blank=False)
    name = models.CharField(max_length=30, blank=True)
    logo = models.URLField(blank=True)
    isOnline = models.BooleanField(blank=False)

    coreCoordinator = models.ForeignKey(Student, models.RESTRICT, blank=False, related_name='CoreCoordinator')
    coordinator = models.ForeignKey(Student, models.RESTRICT, blank=False, related_name='Coordinator')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='subEvent_primary_key_constraint',
                fields=['eventID', 'subEventID']
            )
        ]