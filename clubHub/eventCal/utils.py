from schedule.models import Calendar, Event, Rule

from datetime import datetime

def createCalendar(calendarName: str, calendarDescription: str):
    cal = Calendar(name=calendarDescription, slug=calendarName)
    cal.save()
    try:
        rule = Rule.objects.get(name="Daily")
    except Rule.DoesNotExist:
        rule = Rule(frequency="YEARLY", name="Yearly", description="will recur once every Year")
        rule.save()
        rule = Rule(frequency="MONTHLY", name="Monthly", description="will recur once every Month")
        rule.save()
        rule = Rule(frequency="WEEKLY", name="Weekly", description="will recur once every Week")
        rule.save()
        rule = Rule(frequency="DAILY", name="Daily", description="will recur once every Day")
        rule.save()