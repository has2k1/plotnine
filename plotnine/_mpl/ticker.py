import locale

from matplotlib.ticker import FixedFormatter


class MyFixedFormatter(FixedFormatter):
    """
    Override MPL fixedformatter for better formatting
    """

    def format_data(self, value: float) -> str:
        """
        Return a formatted string representation of a number.
        """
        s = locale.format_string("%1.10e", (value,))
        return self.fix_minus(s)
