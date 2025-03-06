from django.utils import timezone


def is_valid_date(date):
    try:
        timezone.datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    
def is_valid_weekday(weekday):
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if weekday.lower() in weekdays:
        return True
    return False

now = timezone.now()

# Start of the current day
start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

# Start of the current week (Monday)
start_of_week = start_of_day - timezone.timedelta(days=now.weekday())

# Start of the current month
start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

# Start of the current year
start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)