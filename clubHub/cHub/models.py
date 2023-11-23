from django.db import models
from django.core.exceptions import ValidationError

dummyImage = "https://dummyimage.com/500&text=Image+not+Found"

class Branch(models.Model):
    """A Django Model representing a Branch."""
    id = models.CharField(primary_key=True, max_length=4)
    name = models.CharField(blank=False, max_length=30)

    def __str__(self):
        return f"{self.name} ({self.id})"
    
class Student(models.Model):
    """A Django Model representing a Student."""
    roll_no = models.PositiveIntegerField(blank=False)
    branch_id = models.ForeignKey('Branch', models.RESTRICT, blank=False)
    batch_no = models.PositiveIntegerField(blank=False)
    name = models.CharField(max_length=30, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='student_primary_key_constraint',
                fields=['roll_no', 'branch_id', 'batch_no']
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.batch_no} {self.branch_id.name} {str(self.roll_no).zfill(3)})"
    
class Club(models.Model):
    """A Django Model representing a Club."""
    club_id = models.CharField(blank=False, max_length=10)
    club_year = models.PositiveIntegerField(blank=False)
    club_name = models.CharField(blank=False, max_length=50)
    topic = models.CharField(blank=False, max_length=50)
    faculty_mentor = models.CharField(max_length=50)
    logo = models.URLField(default=dummyImage)
    faculty_mentor_picture = models.URLField(default=dummyImage)

    president_id = models.ForeignKey('Student', models.RESTRICT, blank=False, related_name='president')
    vice_president_id = models.ForeignKey('Student', models.RESTRICT, blank=False, related_name='vice_president')
    president_picture = models.URLField(default=dummyImage)
    vice_president_picture = models.URLField(default=dummyImage)

    def clean(self):
        if self.president_id != None and self.president_id == self.vice_president_id:
            raise ValidationError('A Student cannot be both President & Vice-President.', 'invalid')
        
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='club_primary_key_constraint',
                fields=['club_id', 'club_year', 'topic']
            )
        ]

    def __str__(self):
        return f"{self.topic} - {self.club_year} ({self.club_name})"
    
class ClubMember(models.Model):
    """A Django Model representing the Coordinators of a Club."""
    club_id = models.ForeignKey(Club, models.RESTRICT, blank=False)
    member = models.ForeignKey(Student, models.RESTRICT, blank=False)
    role = models.CharField(default='Volunteer', max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='clubMember_primary_key_constraint',
                fields=['club_id', 'member', 'role']
            )
        ]

    def __str__(self):
        return f"{self.club_id} - {self.role} {self.member}"