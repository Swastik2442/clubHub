from datetime import datetime
import os, logging

from schedule.models import Calendar, Rule, Event
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
calendarName = os.getenv('CALENDAR_NAME')

def createCalendar(calendarName: str, calendarDescription: str):
    """Creates a Calendar if One does not Exists."""
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

def addEvent(eventName: str, eventStartDate: datetime, eventEndDate: datetime = None, eventRepetition: str = '', eventColour: str = ''):
    """Adds an Event to the Event Calendar provided."""
    success = False
    repetitionRule = None

    if eventRepetition != '':
        try:
            repetitionRule = Rule.objects.get(frequency=eventRepetition)
        except Exception:
            return False

    if eventEndDate == None:
        eventEndDate = eventStartDate

    data = {
        'title': eventName,
        'start': eventStartDate,
        'end': eventEndDate,
        'color_event': eventColour,
        'rule': repetitionRule,
        'calendar': Calendar.objects.get(slug=calendarName)
    }
    try:
        Event.objects.get(title=data['title'], start=data['start'], end=data['end'])
        success = True
    except Exception as err:
        print(err)
        pass
    
    if not success:
        try:
            sEvent = Event(**data)
            sEvent.save()
            success = True
        except Exception as err:
            print(err)
            logger.warning(err)
    return success