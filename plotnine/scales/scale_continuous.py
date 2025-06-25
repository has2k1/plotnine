from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence, cast
from warnings import warn

import numpy as np
import pandas as pd
from mizani.bounds import censor, expand_range_distinct, rescale, zero_range
from mizani.palettes import identity_pal

from .._utils import match
from ..exceptions import PlotnineError, PlotnineWarning
from ..iapi import range_view, scale_view
from ._expand import expand_range
from ._runtime_typing import (
    ContinuousBreaksUser,
    ContinuousLimitsUser,
    GuideTypeT,
    MinorBreaksUser,
    TransUser,
)
from .range import RangeContinuous
from .scale import scale

if TYPE_CHECKING:
    from typing import Optional

    from mizani.transforms import trans
    from mizani.typing import PCensor, PRescale

    from plotnine.typing import (
        CoordRange,
        FloatArrayLike,
        TFloatArrayLike,
    )


@dataclass(kw_only=True)
class scale_continuous(
    scale[
        RangeContinuous,
        ContinuousBreaksUser,
        ContinuousLimitsUser,
        # subclasses are still generic and must specify the
        # type of the guide
        GuideTypeT,
    ]
):
    """
    Base class for all continuous scales

    Notes
    -----
    If using the class directly all arguments must be
    keyword arguments.
    """

    limits: ContinuousLimitsUser = None
    """
    Limits of the scale. Most commonly, these are the minimum & maximum
    values for the scale. If not specified they are derived from the data.
    It may also be a function that takes the derived limits and transforms
    them into the final limits.
    """

    rescaler: PRescale = rescale
    """
    Function to rescale data points so that they can be handled by the
    palette. Default is to rescale them onto the [0, 1] range. Scales
    that inherit from this class may have another default.
    """

    oob: PCensor = censor
    """
    Function to deal with out of bounds (limits) data points. Default
    is to turn them into `np.nan`, which then get dropped.
    """

    breaks: ContinuousBreaksUser = True
    """
    Major breaks
    """

    minor_breaks: MinorBreaksUser = True
    """
    If a list-like, it is the minor breaks points. If an integer, it is the
    number of minor breaks between any set of major breaks.
    If a function, it should have the signature `func(limits)` and return a
    list-like of consisting of the minor break points.
    If `None`, no minor breaks are calculated. The default is to automatically
    calculate them.
    """

    trans: TransUser = None
    """
    The transformation of the scale. Either name of a trans function or
    a trans function. See [](`mizani.transforms`) for possible options.
    """

    def __post_init__(self):
        super().__post_init__()
        self._range = RangeContinuous()
        self._trans = self._make_trans()
        self.limits = self._prep_limits(self.limits)

    def _prep_limits(
        self, value: ContinuousLimitsUser
    ) -> ContinuousLimitsUser:
        """
        Limits for the continuous scale

        Parameters
        ----------
        value : array_like | callable
            Limits in the dataspace.
        """
        # Notes
        # -----
        # The limits are given in original dataspace
        # but they are stored in transformed space since
        # all computations happen on transformed data. The
        # labeling of the plot axis and the guides are in
        # the original dataspace.
        if isinstance(value, bool) or value is None or callable(value):
            return value

        a, b = value
        a = self.transform([a])[0] if a is not None else a
        b = self.transform([b])[0] if b is not None else b

        if a is not None and b is not None and a > b:
            a, b = b, a

        return a, b

    def _make_trans(self) -> trans:
        """
        Return a valid transform object

        When scales specialise on a specific transform (other than
        the identity transform), the user should know when they
        try to change the transform.

        Parameters
        ----------
        t : mizani.transforms.trans
            Transform object
        """
        from mizani.transforms import gettrans

        t = gettrans(self.trans if self.trans else self.__class__.trans)

        orig_trans_name = self.__class__.trans
        new_trans_name = t.__class__.__name__
        if new_trans_name.endswith("_trans"):
            new_trans_name = new_trans_name[:-6]

        if orig_trans_name not in {None, "identity", new_trans_name}:
            warn(
                "You have changed the transform of a specialised scale. "
                "The result may not be what you expect.\n"
                "Original transform: {}\n"
                "New transform: {}".format(orig_trans_name, new_trans_name),
                PlotnineWarning,
                stacklevel=1,
            )

        return t

    @property
    def final_limits(self) -> tuple[float, float]:
        if self.is_empty():
            return (0, 1)

        if self.limits is None:
            return self._range.range
        elif callable(self.limits):
            # Function works in the dataspace, but the limits are
            # stored in transformed space. The range of the scale is
            # in transformed space (i.e. with in the domain of the scale)
            _range = self.inverse(self._range.range)
            return self.transform(self.limits(_range))
        elif (
            self.limits is not None
            and not self._range.is_empty()
            and
            # Fall back to the range if the limits
            # are not set or if any is None or NaN
            len(self.limits) == len(self._range.range)
        ):
            l1, l2 = self.limits
            r1, r2 = self._range.range
            if l1 is None:
                l1 = self.transform([r1])[0]
            if l2 is None:
                l2 = self.transform([r2])[0]
            return l1, l2

        return self.limits

    def train(self, x: FloatArrayLike):
        """
        Train continuous scale
        """
        if not len(x):
            return

        self._range.train(x)

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform dataframe
        """
        if len(df) == 0:
            return df

        aesthetics = set(self.aesthetics) & set(df.columns)
        for ae in aesthetics:
            with suppress(TypeError):
                df[ae] = self.transform(df[ae])

        return df

    def transform(self, x: TFloatArrayLike) -> TFloatArrayLike:
        """
        Transform array|series x
        """
        return self._trans.transform(x)

    def inverse_df(self, df):
        """
        Inverse Transform dataframe
        """
        if len(df) == 0:
            return df

        aesthetics = set(self.aesthetics) & set(df.columns)
        for ae in aesthetics:
            with suppress(TypeError):
                df[ae] = self.inverse(df[ae])

        return df

    def inverse(self, x: TFloatArrayLike) -> TFloatArrayLike:
        """
        Inverse transform array|series x
        """
        return self._trans.inverse(x)

    @property
    def is_linear_scale(self) -> bool:
        """
        Return True if the scale is linear

        Depends on the transformation.
        """
        return self._trans.transform_is_linear

    @property
    def domain_is_numerical(self) -> bool:
        """
        Return True if transformation acts on numerical data.

        Depends on the transformation.
        """
        return self._trans.domain_is_numerical

    @property
    def is_log_scale(self) -> bool:
        """
        Return True if the scale is log transformationed
        """
        return hasattr(
            self._trans, "base"
        ) and self._trans.__class__.__name__.startswith("log")

    def dimension(self, expand=(0, 0, 0, 0), limits=None):
        """
        Get the phyical size of the scale

        Unlike limits, this always returns a numeric vector of length 2
        """
        if limits is None:
            limits = self.final_limits
        return expand_range_distinct(limits, expand)

    def expand_limits(
        self,
        limits: tuple[float, float],
        expand: tuple[float, float] | tuple[float, float, float, float],
        coord_limits: CoordRange | None,
        trans: trans,
    ) -> range_view:
        """
        Calculate the final range in coordinate space
        """
        # - Override None in coord_limits
        # - Expand limits in coordinate space
        # - Remove any computed infinite values &
        if coord_limits is not None:
            c0, c1 = coord_limits
            limits = (
                limits[0] if c0 is None else c0,
                limits[1] if c1 is None else c1,
            )
        return expand_range(limits, expand, trans)

    def view(
        self,
        limits: Optional[CoordRange] = None,
        range: Optional[CoordRange] = None,
    ) -> scale_view:
        """
        Information about the trained scale
        """
        if limits is None:
            limits = self.final_limits

        if range is None:
            range = self.dimension(limits=limits)

        breaks = self.get_bounded_breaks(range)
        labels = self.get_labels(breaks)

        ubreaks = self.get_breaks(range)
        minor_breaks = self.get_minor_breaks(ubreaks, range)

        sv = scale_view(
            scale=self,
            aesthetics=self.aesthetics,
            name=self.name,
            limits=limits,
            range=range,
            breaks=breaks,
            labels=labels,
            minor_breaks=minor_breaks,
        )
        return sv

    def default_expansion(self, mult=0.05, add=0, expand=True):
        """
        Get the default expansion for continuous scale
        """
        # Continuous scales have transforms, some of which may be on
        # domains that are not numeric, and the diffs on these domains
        # are not numeric as well. To do arithmetic (+/-) that uses diff
        # value, we need diff values represented as suitable numerical
        # values.
        if not expand:
            return (0, 0, 0, 0)

        def to_num(x) -> float:
            # For now this function assume that if the user passes in
            # a numeric value (for any kind for scale), they know what
            # they are doing. Usually this will be a 0.
            return (
                x
                if isinstance(x, (float, int))
                else self._trans.diff_type_to_num([x])[0]
            )

        if (exp := self.expand) is None:
            m1, m2 = mult if isinstance(mult, (tuple, list)) else (mult, mult)
            _add = add if isinstance(add, (tuple, list)) else (add, add)
            a1, a2 = to_num(_add[0]), to_num(_add[1])
            exp = (m1, a1, m2, a2)
        elif len(exp) == 2:
            exp = exp[0], to_num(exp[1])
            exp = (*exp, *exp)
        else:  # exp is a tuple with 4 elements
            exp = exp[0], to_num(exp[1]), exp[2], to_num(exp[3])

        return exp

    def palette(self, x):
        """
        Map an data values to values of the scale
        """
        return identity_pal()(x)

    def map(
        self, x: FloatArrayLike, limits: Optional[tuple[float, float]] = None
    ) -> FloatArrayLike:
        if limits is None:
            limits = self.final_limits

        x = self.oob(self.rescaler(x, _from=limits))
        na_value = cast("float", self.na_value)

        uniq = np.unique(x)
        pal = np.asarray(self.palette(uniq))
        scaled = pal[match(x, uniq)]
        if scaled.dtype.kind == "U":
            scaled = [na_value if x == "nan" else x for x in scaled]
        else:
            scaled[pd.isna(scaled)] = na_value
        return scaled

    def get_breaks(
        self, limits: Optional[tuple[float, float]] = None
    ) -> Sequence[float]:
        """
        Generate breaks for the axis or legend

        Parameters
        ----------
        limits : list_like | None
            If None the self.limits are used
            They are expected to be in transformed
            space.

        Returns
        -------
        out : array_like

        Notes
        -----
        Breaks are calculated in data space and
        returned in transformed space since all
        data is plotted in transformed space.
        """
        if limits is None:
            limits = self.final_limits

        # To data space
        _limits = self.inverse(limits)

        if self.is_empty() or self.breaks is False or self.breaks is None:
            breaks = []
        elif self.breaks is True:
            # TODO: Fix this type mismatch in mizani with
            # a typevar so that type-in = type-out
            _tlimits = self._trans.breaks(_limits)
            breaks: Sequence[float] = _tlimits  # pyright: ignore
        elif zero_range(_limits):
            breaks = [_limits[0]]
        elif callable(self.breaks):
            breaks = self.breaks(_limits)
        else:
            breaks = self.breaks

        breaks = self.transform(breaks)
        return breaks

    def get_bounded_breaks(
        self, limits: Optional[tuple[float, float]] = None
    ) -> Sequence[float]:
        """
        Return Breaks that are within limits
        """
        if limits is None:
            limits = self.final_limits
        breaks = self.get_breaks(limits)
        strict_breaks = [b for b in breaks if limits[0] <= b <= limits[1]]
        return strict_breaks

    def get_minor_breaks(
        self,
        major: Sequence[float],
        limits: Optional[tuple[float, float]] = None,
    ) -> Sequence[float]:
        """
        Return minor breaks
        """
        if limits is None:
            limits = self.final_limits

        if self.minor_breaks is False or self.minor_breaks is None:
            minor_breaks = []
        elif self.minor_breaks is True:
            minor_breaks: Sequence[float] = self._trans.minor_breaks(
                major, limits
            )  # pyright: ignore
        elif isinstance(self.minor_breaks, int):
            minor_breaks: Sequence[float] = self._trans.minor_breaks(
                major,
                limits,
                self.minor_breaks,  # pyright: ignore
            )
        elif callable(self.minor_breaks):
            breaks = self.minor_breaks(self.inverse(limits))
            _major = set(major)
            minor = self.transform(breaks)
            minor_breaks = [x for x in minor if x not in _major]
        else:
            minor_breaks = self.transform(self.minor_breaks)

        return minor_breaks

    def get_labels(
        self, breaks: Optional[Sequence[float]] = None
    ) -> Sequence[str]:
        """
        Generate labels for the axis or legend

        Parameters
        ----------
        breaks: None | array_like
            If None, use self.breaks.
        """
        if breaks is None:
            breaks = self.get_breaks()

        breaks = self.inverse(breaks)
        labels: Sequence[str]

        if self.labels is False or self.labels is None:
            labels = []
        elif self.labels is True:
            labels = self._trans.format(breaks)
        elif callable(self.labels):
            labels = self.labels(breaks)
        elif isinstance(self.labels, dict):
            labels = [
                str(self.labels[b]) if b in self.labels else str(b)
                for b in breaks
            ]
        else:
            # When user sets breaks and labels of equal size,
            # but the limits exclude some of the breaks.
            # We remove the corresponding labels
            from collections.abc import Iterable, Sized

            labels = self.labels
            if (
                len(labels) != len(breaks)
                and isinstance(self.breaks, Iterable)
                and isinstance(self.breaks, Sized)
                and len(labels) == len(self.breaks)
            ):
                _wanted_breaks = set(breaks)
                labels = [
                    l
                    for l, b in zip(labels, self.breaks)
                    if b in _wanted_breaks
                ]

        if len(labels) != len(breaks):
            raise PlotnineError("Breaks and labels are different lengths")

        return labels
