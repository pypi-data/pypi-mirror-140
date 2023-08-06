import time, click, sys

@click.command()
def cdate():
    parts = time.ctime().split(' ')
    day = parts[0]
    month = parts[1]
    date = parts[2] if parts[2] != ' ' and parts[2] != '' else parts[3]
    year = parts[4] if parts[2] != ' ' and parts[2] != '' else parts[5]

    if day == 'Mon':
        day = 'Monday'
    elif day == 'Tue':
        day = 'Tuesday'
    elif day == 'Wed':
        day = 'Wednesday'
    elif day == 'Thu':
        day = 'Thursday'
    elif day == 'Fri':
        day = 'Friday'
    elif day == 'Sat':
        day = 'Saturday'
    elif day == 'Sun':
        day = 'Sunday'

    if month == 'Jan':
        month = '01'
    elif month == 'Feb':
        month = '02'
    elif month == 'Mar':
        month = '03'
    elif month == 'Apr':
        month = '04'
    elif month == 'May':
        month = '05'
    elif month == 'Jun':
        month = '06'
    elif month == 'Jul':
        month = '07'
    elif month == 'Aug':
        month = '08'
    elif month == 'Sep':
        month = '09'
    elif month == 'Oct':
        month = '10'
    elif month == 'Nov':
        month = '11'
    elif month == 'Dec':
        month = '12'

    print(f'{day} {date}/{month}/{year}')

@click.command()
def ctime():
    while True:
        parts = time.ctime().split(' ')

        currentTime = parts[3] if parts[2] != ' ' and parts[2] != '' else parts[4]

        sys.stdout.write('\r')
        sys.stdout.write(currentTime)
        sys.stdout.flush()
        time.sleep(1)

@click.command()
def cdatetime():
    while True:
        parts = time.ctime().split(' ')
        day = parts[0]
        month = parts[1]
        date = parts[2] if parts[2] != ' ' and parts[2] != '' else parts[3]
        year = parts[4] if parts[2] != ' ' and parts[2] != '' else parts[5]

        if day == 'Mon':
            day = 'Monday'
        elif day == 'Tue':
            day = 'Tuesday'
        elif day == 'Wed':
            day = 'Wednesday'
        elif day == 'Thu':
            day = 'Thursday'
        elif day == 'Fri':
            day = 'Friday'
        elif day == 'Sat':
            day = 'Saturday'
        elif day == 'Sun':
            day = 'Sunday'

        if month == 'Jan':
            month = '01'
        elif month == 'Feb':
            month = '02'
        elif month == 'Mar':
            month = '03'
        elif month == 'Apr':
            month = '04'
        elif month == 'May':
            month = '05'
        elif month == 'Jun':
            month = '06'
        elif month == 'Jul':
            month = '07'
        elif month == 'Aug':
            month = '08'
        elif month == 'Sep':
            month = '09'
        elif month == 'Oct':
            month = '10'
        elif month == 'Nov':
            month = '11'
        elif month == 'Dec':
            month = '12'

        currentTime = parts[3] if parts[2] != ' ' and parts[2] != '' else parts[4]

        sys.stdout.write('\r')
        sys.stdout.write(f'{day} {date}/{month}/{year} {currentTime}')
        sys.stdout.flush()
        time.sleep(1)