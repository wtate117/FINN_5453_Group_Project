from common_imports import datetime, relativedelta, date



'''
Across all the functions both the start_date and end_date are returned    
    The start_date is what the functions are designed to find
    The end_date is the current day
'''


def get_start_date(time_unit = 'y', time_frame = 1):
    time_unit = time_unit.upper()
    if(time_unit == 'Y'):
        end_date, start_date = date_years_back(time_frame)
    elif(time_unit == 'M'):
        end_date, start_date = date_months_back(time_frame)
    elif(time_unit == 'D'):
        end_date, start_date = date_days_back(time_frame)
    elif(time_unit == 'YTD'):
        end_date = date.today()
        start_date = january_first_of_year(end_date)

    else:
        end_date, start_date = date_years_back(time_frame)

    return end_date, start_date


# Function to calculate the date x years before today, with leap year handling
def date_years_back(increment):
    # Get today's date
    today = date.today()
    increment = int(increment)
    try:
        # Calculate the date x years ago
        x_years_ago = today - relativedelta(years=increment)
    except ValueError:
        # Handles the case for February 29 on a leap year
        # Adjusts the date to February 28
        x_years_ago = today - relativedelta(years=increment, days=1)

    return today, x_years_ago

# returns the date today and three months ago for the risk free rate
def date_months_back(increment):
    # Get today's date
    today = date.today()
    # Calculate the date three months before today
    try:
        x_months_ago = today - relativedelta(months=increment)
    except ValueError:
        # Handles the case for February 29 on a leap year
        # Adjusts the date to February 28
        x_months_ago = today - relativedelta(months=increment, days=1)

    return today, x_months_ago

def date_days_back(increment):
    # Get today's date
    today = date.today()
    # Calculate the date three months before today
    try:
        x_days_ago = today - relativedelta(days=increment)
    except ValueError:
        # Handles the case for February 29 on a leap year
        # Adjusts the date to February 28
        x_days_ago = today - relativedelta(days=(increment - 1))

    return today, x_days_ago


from datetime import datetime

def january_first_of_year(date):
    """
    Given a datetime.date or datetime.datetime object, returns a datetime.date object
    for January 1 of the same year.

    Args:
    date (datetime.date or datetime.datetime): The date from which the year will be extracted.

    Returns:
    datetime.date: A date object representing January 1 of the extracted year.
    """
    # Extract the year from the provided date
    year = date.year
    # Create a new date object for January 1st of the extracted year
    january_first = datetime(year, 1, 1).date()
    return january_first

# Example usage



