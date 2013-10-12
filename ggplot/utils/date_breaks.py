from matplotlib.dates import DayLocator, WeekdayLocator, MonthLocator

class YearLocator(MonthLocator):
    """
    unclear why this is even necessary. if you know, please explain
    it to me => austin at yhathq dot com.
    """
    def __init__(self, interval):
        "show ticks ever n years."
        interval = interval * 12
        super(YearLocator, self).__init__(interval=interval)

def parse_break_str(txt):
    "parses '10 weeks' into tuple (10, week)."
    txt = txt.strip()
    if len(txt.split()) == 2:
        n, units = txt.split()
    else:
        n,units = 1, txt
    units = units.rstrip('s') # e.g. weeks => week
    n = int(n)
    return n, units

LOCATORS = {
    'day': DayLocator,
    'week': WeekdayLocator,
    'month': MonthLocator,
    'year': YearLocator
}

def date_breaks(breaks):
    period, units = parse_break_str(breaks)
    Locator = LOCATORS.get(units)
    locator = Locator(interval=period)
    return locator
