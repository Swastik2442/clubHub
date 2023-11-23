from django.db import models
from cHub.models import Student, Club

RepetitionTypes = models.TextChoices("RepetitionTypes", "DAILY WEEKLY MONTHLY YEARLY NULL")

class Event(models.Model):
    """A Django Model representing an Event."""
    id = models.CharField(primary_key=True, max_length=4)
    name = models.CharField(max_length=30, blank=False)
    startDate = models.DateTimeField(blank=False)
    endDate = models.DateTimeField(blank=True, null=True)
    logo = models.URLField(blank=True)
    location = models.CharField(blank=True, max_length=50)
    isOnline = models.BooleanField(blank=False)
    organizingHead = models.ForeignKey(Student, models.RESTRICT, blank=True, null=True)
    repetition = models.CharField(max_length=7, blank=False, default="NULL", choices=RepetitionTypes.choices)

    def __str__(self):
        return f"{self.name} ({self.startDate.year})"

class EventSession(models.Model):
    """A Django Model representing the Sessions of Events."""
    eventID = models.ForeignKey(Event, models.RESTRICT, blank=False)
    sessionID = models.CharField(max_length=4, blank=False)
    sessionName = models.CharField(max_length=20, blank=True)
    startDate = models.DateTimeField(blank=False)
    endDate = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='session_primary_key_constraint',
                fields=['eventID', 'sessionID']
            )
        ]

    def __str__(self):
        return f"{self.sessionName} ({self.eventID})"

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

    def __str__(self):
        return f"{self.eventID} - {self.member}"

class EventOperationsTeam(models.Model):
    """A Django Model representing the Operations Team of an Event."""
    eventID = models.ForeignKey(Event, models.RESTRICT, blank=False)
    teamID = models.CharField(max_length=4, blank=False)
    name = models.CharField(max_length=20, blank=False)
    coreCoordinator = models.ForeignKey(Student, models.RESTRICT)
    relatedClub = models.ForeignKey(Club, models.RESTRICT, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='operations_primary_key_constraint',
                fields=['eventID', 'teamID']
            )
        ]

    def __str__(self):
        return f"{self.eventID} - {self.name} Team"

class SubEvent(models.Model):
    """A Django Model representing the Sub-Events in an Event (if any)."""
    eventID = models.ForeignKey(Event, models.RESTRICT, blank=False)
    subEventID = models.CharField(max_length=4, blank=False)
    name = models.CharField(max_length=30, blank=True)
    logo = models.URLField(blank=True)
    startDate = models.DateTimeField(blank=False)
    endDate = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=50)
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
    
    def __str__(self):
        return f"{self.name} ({self.eventID})"