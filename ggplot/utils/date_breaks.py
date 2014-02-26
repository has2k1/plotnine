from matplotlib.dates import DayLocator, WeekdayLocator, MonthLocator, YearLocator

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

# matplotlib's YearLocator uses different named
# arguments than the others
LOCATORS = {
    'day': DayLocator,
    'week': WeekdayLocator,
    'month': MonthLocator,
    'year': lambda interval: YearLocator(base=interval)
}

def date_breaks(width):
    """
    "Regularly spaced dates."

    width:
        an interval specification. must be one of [day, week, month, year]
    usage:
        date_breaks(width = '1 year')
        date_breaks(width = '6 weeks')
        date_breaks('months')
    """
    period, units = parse_break_str(width)
    Locator = LOCATORS.get(units)
    locator = Locator(interval=period)
    return locator
