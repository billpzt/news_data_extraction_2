from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

def date_formatter(date_str):
    try:
        # Parse the input date string with the current year appended
        complete_date_str = f"{date_str} {datetime.now().year}"
        date = datetime.strptime(complete_date_str, '%B %d %Y')
    except ValueError:
        # Fallback to today's date if parsing fails
        date = datetime.today()
        
    # Return only the date part
    return date.date()

from datetime import datetime
from dateutil.parser import parse

def date_formatter_parse(date_str):
    try:
        # Attempt to parse the input date string
        parsed_date = parse(date_str)
        # If successful, return the date part of the parsed date
        return parsed_date.date()
    except ValueError:
        # If parsing fails, return today's date
        return datetime.today().date()

# print(date_formatter_parse('May 24'))
# print('14 Hours ago')
# print(date_formatter('invalid date string'))

print(date_formatter_parse('May 24'))
print(date_formatter_parse('14 Hours ago'))
print(date_formatter_parse('June 6, 2022'))