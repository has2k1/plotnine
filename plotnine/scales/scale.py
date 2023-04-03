from __future__ import annotations

import typing
from contextlib import suppress
from copy import copy, deepcopy
from warnings import warn

import numpy as np
import pandas as pd
from mizani.bounds import censor, expand_range_distinct, rescale, zero_range

from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
from ..iapi import range_view, scale_view
from ..mapping.aes import is_position_aes, rename_aesthetics
from ..utils import Registry, match
from ._expand import expand_range
from .range import Range, RangeContinuous, RangeDiscrete

if typing.TYPE_CHECKING:
    from typing import Any, Optional, Sequence, Type

    from plotnine.typing import (
        AnyArrayLike,
        CoordRange,
        FloatArrayLike,
        FloatArrayLikeTV,
        ScaleBreaks,
        ScaleBreaksRaw,
        ScaleContinuousBreaks,
        ScaleContinuousBreaksRaw,
        ScaleContinuousLimits,
        ScaleContinuousLimitsRaw,
        ScaledAestheticsName,
        ScaleDiscreteBreaks,
        ScaleDiscreteBreaksRaw,
        ScaleDiscreteLimits,
        ScaleDiscreteLimitsRaw,
        ScaleLabels,
        ScaleLabelsRaw,
        ScaleLimits,
        ScaleLimitsRaw,
        ScaleMinorBreaksRaw,
        Trans,
        TupleFloat2,
        TupleFloat4,
    )


class scale(metaclass=Registry):
    """
    Base class for all scales

    Parameters
    ----------
    breaks : array_like or callable, optional
        Major break points. Alternatively, a callable that
        takes a tuple of limits and returns a list of breaks.
        Default is to automatically calculate the breaks.
    expand : tuple, optional
        Multiplicative and additive expansion constants
        that determine how the scale is expanded. If
        specified must be of length 2 or 4. Specifically the
        values are in this order::

            (mul, add)
            (mul_low, add_low, mul_high, add_high)

        For example,

            - ``(0, 0)`` - Do not expand.
            - ``(0, 1)`` - Expand lower and upper limits by 1 unit.
            - ``(1, 0)`` - Expand lower and upper limits by 100%.
            - ``(0, 0, 0, 0)`` - Do not expand, as ``(0, 0)``.
            - ``(0, 0, 0, 1)`` - Expand upper limit by 1 unit.
            - ``(0, 1, 0.1, 0)`` - Expand lower limit by 1 unit and
              upper limit by 10%.
            - ``(0, 0, 0.1, 2)`` - Expand upper limit by 10% plus
              2 units.

        If not specified, suitable defaults are chosen.
    name : str, optional
        Name used as the label of the scale. This is what
        shows up as the axis label or legend title. Suitable
        defaults are chosen depending on the type of scale.
    labels : list or callable, optional
        List of :class:`str`. Labels at the `breaks`.
        Alternatively, a callable that takes an array_like of
        break points as input and returns a list of strings.
    limits : array_like, optional
        Limits of the scale. Most commonly, these are the
        min & max values for the scales. For scales that
        deal with categoricals, these may be a subset or
        superset of the categories.
    na_value : scalar
        What value to assign to missing values. Default
        is to assign ``np.nan``.
    palette : callable, optional
        Function to map data points onto the scale. Most
        scales define their own palettes.
    aesthetics : list, optional
        list of :class:`str`. Aesthetics covered by the
        scale. These are defined by each scale and the
        user should probably not change them. Have fun.
    """

    __base__ = True

    # aesthetics affected by this scale
    _aesthetics: list[ScaledAestheticsName] = []

    # What to do with the NA values
    na_value: Any = np.nan

    # used as the axis label or legend title
    name: str | None = None

    # major breaks
    breaks: ScaleBreaksRaw = True

    # labels at the breaks
    labels: ScaleLabelsRaw = True

    # legend or any other guide
    guide: str | None = "legend"

    # (min, max) - set by user
    _limits: ScaleLimitsRaw = None

    #: multiplicative and additive expansion constants
    expand: Optional[TupleFloat2 | TupleFloat4] = None

    # range of aesthetic, instantiated in __init__
    range: Range
    _range_class: type[Range] = Range

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                msg = "{} could not recognise parameter `{}`"
                warn(msg.format(self.__class__.__name__, k), PlotnineWarning)

        self.range = self._range_class()

        if np.iterable(self.breaks) and np.iterable(self.labels):
            if len(self.breaks) != len(self.labels):  # pyright: ignore
                raise PlotnineError("Breaks and labels have unequal lengths")

        if (
            self.breaks is None
            and not is_position_aes(self.aesthetics)
            and self.guide is not None
        ):
            self.guide = None

    @property
    def aesthetics(self):
        return self._aesthetics

    @aesthetics.setter
    def aesthetics(self, value):
        if isinstance(value, str):
            value = [value]
        # TODO: Find a way to make the type checking work
        self._aesthetics = rename_aesthetics(value)  # pyright: ignore

    def __radd__(self, gg):
        """
        Add this scale to ggplot object
        """
        gg.scales.append(copy(self))
        return gg

    @staticmethod
    def palette(n):
        """
        Aesthetic mapping function

        Note that not all scales need to implement/provide a palette.
        For example identity & position scales do not use a palette.
        """
        raise NotImplementedError("Not Implemented")

    def map(self, x, limits=None):
        """
        Map every element of x

        The palette should do the real work, this should
        make sure that sensible values are sent and
        return from the palette.
        """
        raise NotImplementedError("Not Implemented")

    def train(self, x):
        """
        Train scale

        Parameters
        ----------
        x: pd.series | np.array
            a column of data to train over
        """
        raise NotImplementedError("Not Implemented")

    def dimension(self, expand=None, limits=None):
        """
        Get the phyical size of the scale.
        """
        raise NotImplementedError("Not Implemented")

    def expand_limits(
        self,
        limits: ScaleLimits,
        expand: TupleFloat2 | TupleFloat4,
        coord_limits: CoordRange | None,
        trans: Trans | Type[Trans],
    ) -> range_view:
        """
        Exand the limits of the scale
        """
        raise NotImplementedError("Not Implemented")

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform dataframe
        """
        raise NotImplementedError("Not Implemented")

    def transform(self, x):
        """
        Transform array|series x
        """
        raise NotImplementedError("Not Implemented")

    def inverse(self, x):
        """
        Inverse transform array|series x
        """
        raise NotImplementedError("Not Implemented")

    def view(
        self,
        limits: Optional[ScaleLimits] = None,
        range: Optional[CoordRange] = None,
    ) -> scale_view:
        """
        Information about the trained scale
        """
        raise NotImplementedError("Not Implemented")

    def default_expansion(
        self,
        mult: float | TupleFloat2 = 0,
        add: float | TupleFloat2 = 0,
        expand=True,
    ) -> TupleFloat4:
        """
        Get default expansion for this scale
        """
        if not expand:
            return (0, 0, 0, 0)

        if self.expand:
            if len(self.expand) == 2:
                mult, add = self.expand
            else:
                # n == 4:
                mult = self.expand[0], self.expand[2]
                add = self.expand[1], self.expand[3]

        if isinstance(mult, (float, int)):
            mult = (mult, mult)

        if isinstance(add, (float, int)):
            add = (add, add)

        if len(mult) != 2:
            raise ValueError(
                "The scale expansion multiplication factor should "
                "either be a single float, or a tuple of two floats. "
            )

        if len(add) != 2:
            raise ValueError(
                "The scale expansion addition constant should "
                "either be a single float, or a tuple of two floats. "
            )

        return (mult[0], add[0], mult[1], add[1])

    def clone(self):
        return deepcopy(self)

    def reset(self):
        """
        Set the range of the scale to None.

        i.e Forget all the training
        """
        self.range.reset()

    def is_empty(self) -> bool:
        """
        Whether the scale has size information
        """
        if not hasattr(self, "range"):
            return True
        return self.range.is_empty() and self._limits is None

    @property
    def limits(self) -> ScaleLimits:
        raise NotImplementedError("Not Implemented")

    @limits.setter
    def limits(self, value: ScaleLimitsRaw):
        raise NotImplementedError("Not Implemented")

    def train_df(self, df: pd.DataFrame):
        """
        Train scale from a dataframe
        """
        aesthetics = sorted(set(self.aesthetics) & set(df.columns))
        for ae in aesthetics:
            self.train(df[ae])

    def map_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map df
        """
        if len(df) == 0:
            return df

        aesthetics = set(self.aesthetics) & set(df.columns)
        for ae in aesthetics:
            df[ae] = self.map(df[ae])

        return df

    def get_labels(self, breaks: Optional[ScaleBreaks] = None) -> ScaleLabels:
        """
        Get labels, calculating them if required
        """
        raise NotImplementedError()

    def get_breaks(self, limits: Optional[ScaleLimits] = None) -> ScaleBreaks:
        """
        Get Breaks
        """
        raise NotImplementedError()

    def get_bounded_breaks(
        self, limits: Optional[ScaleLimits] = None
    ) -> ScaleBreaks:
        """
        Return Breaks that are within the limits
        """
        raise NotImplementedError()


@document
class scale_discrete(scale):
    """
    Base class for all discrete scales

    Parameters
    ----------
    {superclass_parameters}
    limits : array_like, optional
        Limits of the scale. For scales that deal with
        categoricals, these may be a subset or superset of
        the categories. Data values that are not in the limits
        will be treated as missing data and represented with
        the ``na_value``.
    drop : bool
        Whether to drop unused categories from
        the scale
    na_translate : bool
        If ``True`` translate missing values and show them.
        If ``False`` remove missing values. Default value is
        ``True``
    na_value : object
        If ``na_translate=True``, what aesthetic value should be
        assigned to the missing values. This parameter does not
        apply to position scales where ``nan`` is always placed
        on the right.
    """

    _range_class = RangeDiscrete
    _limits: Optional[ScaleDiscreteLimitsRaw]
    range: RangeDiscrete
    breaks: ScaleDiscreteBreaksRaw
    drop: bool = True  # drop unused factor levels from the scale
    na_translate: bool = True

    @property
    def limits(self) -> ScaleDiscreteLimits:
        if self.is_empty():
            return ("0", "1")

        if self._limits is None:
            return tuple(self.range.range)
        elif callable(self._limits):
            return tuple(self._limits(self.range.range))
        else:
            return tuple(self._limits)

    @limits.setter
    def limits(self, value: ScaleDiscreteLimitsRaw):
        self._limits = value

    @staticmethod
    def palette(n: int) -> Sequence[Any]:
        """
        Aesthetic mapping function
        """
        raise NotImplementedError("Not Implemented")

    def train(self, x, drop=False):
        """
        Train scale

        Parameters
        ----------
        x: pd.series | np.array
            a column of data to train over
        drop : bool
            Whether to drop(not include) unused categories

        A discrete range is stored in a list
        """
        if not len(x):
            return

        na_rm = not self.na_translate
        self.range.train(x, drop, na_rm=na_rm)

    def dimension(self, expand=(0, 0, 0, 0), limits=None):
        """
        Get the phyical size of the scale

        Unlike limits, this always returns a numeric vector of length 2
        """
        if limits is None:
            limits = self.limits
        return expand_range_distinct(self.limits, expand)

    def expand_limits(
        self,
        limits: ScaleDiscreteLimits,
        expand: TupleFloat2 | TupleFloat4,
        coord_limits: TupleFloat2,
        trans: Trans,
    ) -> range_view:
        """
        Calculate the final range in coordinate space
        """
        # Turn discrete limits into a tuple of continuous limits
        is_empty = self.is_empty() or len(limits) == 0
        climits = (0, 1) if is_empty else (1, len(limits))
        if coord_limits is not None:
            # - Override None in coord_limits
            # - Expand limits in coordinate space
            # - Remove any computed infinite values &
            c0, c1 = coord_limits
            climits = (
                climits[0] if c0 is None else c0,
                climits[1] if c1 is None else c1,
            )
        return expand_range(climits, expand, trans)

    def view(
        self,
        limits: Optional[ScaleDiscreteLimits] = None,
        range: Optional[CoordRange] = None,
    ) -> scale_view:
        """
        Information about the trained scale
        """
        if limits is None:
            limits = self.limits

        if range is None:
            range = self.dimension(limits=limits)

        breaks_d = self.get_breaks(limits)
        breaks = self.map(pd.Categorical(breaks_d))
        minor_breaks = []
        labels = self.get_labels(breaks_d)

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

    def default_expansion(self, mult=0, add=0.6, expand=True):
        """
        Get the default expansion for a discrete scale
        """
        return super().default_expansion(mult, add, expand)

    def map(
        self, x, limits: Optional[ScaleDiscreteLimits] = None
    ) -> Sequence[Any]:
        """
        Map values in x to a palette
        """
        if limits is None:
            limits = self.limits

        n = sum(~pd.isnull(list(limits)))
        pal = self.palette(n)
        if isinstance(pal, dict):
            # manual palette with specific assignments
            pal_match = []
            for val in x:
                try:
                    pal_match.append(pal[val])
                except KeyError:
                    pal_match.append(self.na_value)
        else:
            if not isinstance(pal, np.ndarray):
                pal = np.asarray(pal, dtype=object)
            idx = np.asarray(match(x, limits))
            try:
                pal_match = [pal[i] if i >= 0 else None for i in idx]
            except IndexError:
                # Deal with missing data
                # - Insert NaN where there is no match
                pal = np.hstack((pal.astype(object), np.nan))
                idx = np.clip(idx, 0, len(pal) - 1)
                pal_match = list(pal[idx])

        if self.na_translate:
            bool_pal_match = pd.isnull(pal_match)
            if len(bool_pal_match.shape) > 1:
                # linetypes take tuples, these return 2d
                bool_pal_match = bool_pal_match.any(axis=1)
            bool_idx = pd.isnull(x) | bool_pal_match
            if bool_idx.any():
                pal_match = [
                    x if i else self.na_value
                    for x, i in zip(pal_match, ~bool_idx)
                ]

        return pal_match

    def get_breaks(
        self, limits: Optional[ScaleDiscreteLimits] = None
    ) -> ScaleDiscreteBreaks:
        """
        Return an ordered list of breaks

        The form is suitable for use by the guides e.g.
            ['fair', 'good', 'very good', 'premium', 'ideal']
        """
        if limits is None:
            limits = self.limits

        if self.is_empty():
            return []

        if self.breaks is True:
            breaks = list(limits)
        elif self.breaks in (False, None):
            breaks = []
        elif callable(self.breaks):
            breaks = self.breaks(limits)
        else:
            _wanted_breaks = set(self.breaks)
            breaks = [l for l in limits if l in _wanted_breaks]

        return breaks

    def get_bounded_breaks(
        self, limits: Optional[ScaleDiscreteLimits] = None
    ) -> ScaleDiscreteBreaks:
        """
        Return Breaks that are within limits
        """
        if limits is None:
            limits = self.limits

        lookup = set(limits)
        breaks = self.get_breaks()
        strict_breaks = [b for b in breaks if b in lookup]
        return strict_breaks

    def get_labels(
        self, breaks: Optional[ScaleDiscreteBreaks] = None
    ) -> ScaleLabels:
        """
        Generate labels for the legend/guide breaks
        """
        if self.is_empty():
            return []

        if breaks is None:
            breaks = self.get_breaks()

        # The labels depend on the breaks if the breaks.
        # No breaks, no labels
        if breaks in (None, False) or self.labels in (None, False):
            return []
        elif self.labels is True:
            return [str(b) for b in breaks]
        elif callable(self.labels):
            return self.labels(breaks)
        # if a dict is used to rename some labels
        elif isinstance(self.labels, dict):
            labels = [
                str(self.labels[b]) if b in self.labels else str(b)
                for b in breaks
            ]
            return labels
        else:
            return self.labels

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform dataframe
        """
        # Discrete scales do not do transformations
        return df

    def transform(self, x):
        """
        Transform array|series x
        """
        # Discrete scales do not do transformations
        return x


@document
class scale_continuous(scale):
    """
    Base class for all continuous scales

    Parameters
    ----------
    {superclass_parameters}
    trans : str | function
        Name of a trans function or a trans function.
        See :mod:`mizani.transforms` for possible options.
    oob : function
        Function to deal with out of bounds (limits)
        data points. Default is to turn them into
        ``np.nan``, which then get dropped.
    minor_breaks : list-like or int or callable or None
        If a list-like, it is the minor breaks points.
        If an integer, it is the number of minor breaks between
        any set of major breaks.
        If a function, it should have the signature
        ``func(limits)`` and return a list-like of consisting
        of the minor break points.
        If ``None``, no minor breaks are calculated.
        The default is to automatically calculate them.
    rescaler : function, optional
        Function to rescale data points so that they can
        be handled by the palette. Default is to rescale
        them onto the [0, 1] range. Scales that inherit
        from this class may have another default.

    Notes
    -----
    If using the class directly all arguments must be
    keyword arguments.
    """

    _range_class = RangeContinuous
    _limits: Optional[ScaleContinuousLimitsRaw]
    rescaler = staticmethod(rescale)  # Used by diverging & n colour gradients
    oob = staticmethod(censor)  # what to do with out of bounds data points
    breaks: ScaleContinuousBreaksRaw
    minor_breaks: ScaleMinorBreaksRaw = True
    _trans: Trans | str = "identity"  # transform class

    def __init__(self, **kwargs):
        # Make sure we have a transform.
        self.trans = kwargs.pop("trans", self._trans)

        with suppress(KeyError):
            self.limits = kwargs.pop("limits")

        scale.__init__(self, **kwargs)

    def _check_trans(self, t):
        """
        Check if transform t is valid

        When scales specialise on a specific transform (other than
        the identity transform), the user should know when they
        try to change the transform.

        Parameters
        ----------
        t : mizani.transforms.trans
            Transform object
        """
        orig_trans_name = self.__class__._trans
        new_trans_name = t.__class__.__name__
        if new_trans_name.endswith("_trans"):
            new_trans_name = new_trans_name[:-6]
        if orig_trans_name != "identity":
            if new_trans_name != orig_trans_name:
                warn(
                    "You have changed the transform of a specialised scale. "
                    "The result may not be what you expect.\n"
                    "Original transform: {}\n"
                    "New transform: {}".format(
                        orig_trans_name, new_trans_name
                    ),
                    PlotnineWarning,
                )

    @property
    def trans(self) -> Trans:
        return self._trans  # pyright: ignore

    @trans.setter
    def trans(self, value: Trans | str | Type[Trans]):
        from mizani.transforms import gettrans

        t: Trans = gettrans(value)
        self._check_trans(t)
        self._trans = t
        self._trans.aesthetic = self.aesthetics[0]  # pyright: ignore

    @property
    def limits(self):
        if self.is_empty():
            return (0, 1)

        if self._limits is None:
            return self.range.range
        elif callable(self._limits):
            # Function works in the dataspace, but the limits are
            # stored in transformed space. The range of the scale is
            # in transformed space (i.e. with in the domain of the scale)
            _range = self.trans.inverse(self.range.range)
            return tuple(self.trans.transform(self._limits(_range)))
        elif self._limits is not None and not self.range.is_empty():
            # Fall back to the range if the limits
            # are not set or if any is None or NaN
            if len(self._limits) == len(self.range.range):
                return tuple(
                    self.trans.transform(r) if pd.isnull(l) else l
                    for l, r in zip(self._limits, self.range.range)
                )
        return tuple(self._limits)

    @limits.setter
    def limits(self, value: ScaleContinuousLimitsRaw):
        """
        Limits for the continuous scale

        Parameters
        ----------
        value : array-like | callable
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
            self._limits = value
            return

        a, b = value
        a, b = (
            self.trans.transform(a) if a is not None else a,
            self.trans.transform(b) if b is not None else b,
        )
        with suppress(TypeError):
            if a > b:
                a, b = b, a

        self._limits = a, b

    def train(self, x):
        """
        Train scale

        Parameters
        ----------
        x: pd.series | np.array
            a column of data to train over
        """
        if not len(x):
            return

        self.range.train(x)

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

    def transform(self, x: FloatArrayLikeTV) -> FloatArrayLikeTV:
        """
        Transform array|series x
        """
        try:
            return self.trans.transform(x)
        except TypeError:
            return [self.trans.transform(val) for val in x]  # pyright: ignore

    def inverse(self, x: FloatArrayLikeTV) -> FloatArrayLikeTV:
        """
        Inverse transform array|series x
        """
        try:
            return self.trans.inverse(x)
        except TypeError:
            return [self.trans.inverse(val) for val in x]  # pyright: ignore

    def dimension(self, expand=(0, 0, 0, 0), limits=None):
        """
        Get the phyical size of the scale

        Unlike limits, this always returns a numeric vector of length 2
        """
        if limits is None:
            limits = self.limits
        return expand_range_distinct(limits, expand)

    def expand_limits(
        self,
        limits: ScaleContinuousLimits,
        expand: TupleFloat2 | TupleFloat4,
        coord_limits: CoordRange | None,
        trans: Trans,
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
            limits = self.limits

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
        return super().default_expansion(mult, add, expand)

    @staticmethod
    def palette(arr: FloatArrayLike) -> Sequence[Any]:
        """
        Aesthetic mapping function
        """
        raise NotImplementedError("Not Implemented")

    def map(
        self, x: AnyArrayLike, limits: Optional[ScaleContinuousLimits] = None
    ) -> AnyArrayLike:
        if limits is None:
            limits = self.limits

        x = self.oob(self.rescaler(x, _from=limits))

        uniq = np.unique(x)
        pal = np.asarray(self.palette(uniq))
        scaled = pal[match(x, uniq)]
        if scaled.dtype.kind == "U":
            scaled = [self.na_value if x == "nan" else x for x in scaled]
        else:
            scaled[pd.isnull(scaled)] = self.na_value
        return scaled

    def get_breaks(
        self, limits: Optional[ScaleContinuousLimits] = None
    ) -> ScaleContinuousBreaks:
        """
        Generate breaks for the axis or legend

        Parameters
        ----------
        limits : list-like | None
            If None the self.limits are used
            They are expected to be in transformed
            space.

        Returns
        -------
        out : array-like

        Notes
        -----
        Breaks are calculated in data space and
        returned in transformed space since all
        data is plotted in transformed space.
        """
        if limits is None:
            limits = self.limits

        # To data space
        _limits = self.inverse(limits)

        if self.is_empty():
            breaks = []
        elif self.breaks is True:
            # TODO: Fix this type mismatch in mizani with
            # a typevar so that type-in = type-out
            _tlimits = self.trans.breaks(_limits)
            breaks: ScaleContinuousBreaks = _tlimits  # pyright: ignore
        elif self.breaks is False or self.breaks is None:
            breaks = []
        elif zero_range(_limits):
            breaks = [_limits[0]]
        elif callable(self.breaks):
            breaks = self.breaks(_limits)
        else:
            breaks = self.breaks

        breaks = self.transform(breaks)
        return breaks

    def get_bounded_breaks(
        self, limits: Optional[ScaleContinuousLimits] = None
    ) -> ScaleContinuousBreaks:
        """
        Return Breaks that are within limits
        """
        if limits is None:
            limits = self.limits
        breaks = self.get_breaks(limits)
        strict_breaks = [b for b in breaks if limits[0] <= b <= limits[1]]
        return strict_breaks

    def get_minor_breaks(
        self,
        major: ScaleContinuousBreaks,
        limits: Optional[ScaleContinuousLimits] = None,
    ) -> ScaleContinuousBreaks:
        """
        Return minor breaks
        """
        if limits is None:
            limits = self.limits

        if self.minor_breaks is True:
            # TODO: Remove ignore when mizani is static typed
            minor_breaks: ScaleContinuousBreaks = self.trans.minor_breaks(
                major, limits
            )  # pyright: ignore
        elif isinstance(self.minor_breaks, int):
            # TODO: Remove ignore when mizani is static typed
            minor_breaks: ScaleContinuousBreaks = self.trans.minor_breaks(
                major, limits, n=self.minor_breaks
            )  # pyright: ignore
        elif self.minor_breaks in (False, None) or not len(major):
            minor_breaks = []
        elif callable(self.minor_breaks):
            breaks = self.minor_breaks(self.trans.inverse(limits))
            _major = set(major)
            minor = self.trans.transform(breaks)
            minor_breaks = [x for x in minor if x not in _major]
        else:
            minor_breaks = self.minor_breaks

        return minor_breaks

    def get_labels(
        self, breaks: Optional[ScaleContinuousBreaks] = None
    ) -> ScaleLabels:
        """
        Generate labels for the axis or legend

        Parameters
        ----------
        breaks: None or array-like
            If None, use self.breaks.
        """
        if breaks is None:
            breaks = self.get_breaks()

        breaks = self.inverse(breaks)

        if self.labels is True:
            labels: Sequence[str] = self.trans.format(breaks)
        elif self.labels in (False, None):
            labels = []
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
            from collections.abc import Sized

            labels = self.labels
            if (
                len(labels) != len(breaks)
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


@document
class scale_datetime(scale_continuous):
    """
    Base class for all date/datetime scales

    Parameters
    ----------
    date_breaks : str
        A string giving the distance between major breaks.
        For example `'2 weeks'`, `'5 years'`. If specified,
        ``date_breaks`` takes precedence over
        ``breaks``.
    date_labels : str
        Format string for the labels.
        See :ref:`strftime <strftime-strptime-behavior>`.
        If specified, ``date_labels`` takes precedence over
        ``labels``.
    date_minor_breaks : str
        A string giving the distance between minor breaks.
        For example `'2 weeks'`, `'5 years'`. If specified,
        ``date_minor_breaks`` takes precedence over
        ``minor_breaks``.
    {superclass_parameters}
    """

    _trans = "datetime"

    def __init__(self, **kwargs):
        from mizani.breaks import date_breaks
        from mizani.formatters import date_format

        # Permit the use of the general parameters for
        # specifying the format strings
        with suppress(KeyError):
            breaks = kwargs["breaks"]
            if isinstance(breaks, str):
                kwargs["breaks"] = date_breaks(breaks)

        with suppress(KeyError):
            minor_breaks = kwargs["minor_breaks"]
            if isinstance(minor_breaks, str):
                kwargs["minor_breaks"] = date_breaks(minor_breaks)

        # Using the more specific parameters take precedence
        with suppress(KeyError):
            breaks_fmt = kwargs.pop("date_breaks")
            kwargs["breaks"] = date_breaks(breaks_fmt)

        with suppress(KeyError):
            labels_fmt = kwargs.pop("date_labels")
            kwargs["labels"] = date_format(labels_fmt)

        with suppress(KeyError):
            minor_breaks_fmt = kwargs.pop("date_minor_breaks")
            kwargs["minor_breaks"] = date_breaks(minor_breaks_fmt)

        scale_continuous.__init__(self, **kwargs)
