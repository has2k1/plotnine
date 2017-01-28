from mizani.scale import scale_continuous, scale_discrete


class Range(object):
    """
    Base class for all ranges
    """
    #: Holds the range information
    range = None

    def reset(self):
        """
        Reset range
        """
        self.range = None

    def train(self, x):
        """
        Train range
        """
        raise NotImplementedError("Not Implemented.")


class RangeContinuous(Range):
    """
    Continuous Range
    """
    def train(self, x):
        """
        Train continuous range
        """
        self.range = scale_continuous.train(x, self.range)


class RangeDiscrete(Range):
    """
    Discrete Range
    """
    def train(self, x, drop=False):
        """
        Train discrete range
        """
        self.range = scale_discrete.train(x, self.range, drop)
