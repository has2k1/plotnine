from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from ..exceptions import PlotnineError

if TYPE_CHECKING:
    from typing import Callable, Literal, Optional, TypeAlias

    from ..iapi import strip_label_details

    # Function that can facet strips
    StripLabellingFunc: TypeAlias = Callable[
        [strip_label_details], strip_label_details
    ]

    StripLabellingFuncNames: TypeAlias = Literal[
        "label_value", "label_both", "label_context"
    ]

    StripLabellingDict: TypeAlias = (
        dict[str, str] | dict[str, Callable[[str], str]]
    )

    # Can be coerced to a StripLabellingFunc
    CanBeStripLabellingFunc: TypeAlias = (
        StripLabellingFuncNames
        | StripLabellingFunc
        | Callable[[str], str]
        | StripLabellingDict
    )


def label_value(
    label_info: strip_label_details, multi_line: bool = True
) -> strip_label_details:
    """
    Keep value as the label

    Parameters
    ----------
    label_info : strip_label_details
        Label information whose values will be returned
    multi_line : bool
        Whether to place each variable on a separate line

    Returns
    -------
    out : strip_label_details
        Label text strings
    """
    label_info = label_info.copy()

    if not multi_line:
        label_info = label_info.collapse()

    return label_info


def label_both(
    label_info: strip_label_details, multi_line: bool = True, sep: str = ": "
) -> strip_label_details:
    """
    Concatenate the facet variable with the value

    Parameters
    ----------
    label_info : strip_label_details
        Label information to be modified.
    multi_line : bool
        Whether to place each variable on a separate line
    sep : str
        Separation between variable name and value

    Returns
    -------
    out : strip_label_details
        Label information
    """
    label_info = label_info.copy()

    for var, lvalue in label_info.variables.items():
        label_info.variables[var] = f"{var}{sep}{lvalue}"

    if not multi_line:
        label_info = label_info.collapse()

    return label_info


def label_context(
    label_info: strip_label_details, multi_line: bool = True, sep: str = ": "
) -> strip_label_details:
    """
    Create an unabiguous label string

    If facetting over a single variable, `label_value` is
    used, if two or more variables then `label_both` is used.

    Parameters
    ----------
    label_info : strip_label_details
        Label information
    multi_line : bool
        Whether to place each variable on a separate line
    sep : str
        Separation between variable name and value

    Returns
    -------
    out : str
        Concatenated label values (or pairs of variable names
        & values)
    """
    if len(label_info) == 1:
        return label_value(label_info, multi_line)
    else:
        return label_both(label_info, multi_line, sep)


LABELLERS: dict[StripLabellingFuncNames, StripLabellingFunc] = {
    "label_value": label_value,
    "label_both": label_both,
    "label_context": label_context,
}


def as_labeller(
    x: Optional[CanBeStripLabellingFunc] = None,
    default: CanBeStripLabellingFunc = label_value,
    multi_line: bool = True,
) -> labeller:
    """
    Coerse to labeller

    Parameters
    ----------
    x : callable | dict
        Object to coerce
    default : str | callable
        Default labeller. If it is a string,
        it should be the name of one the labelling
        functions provided by plotnine.
    multi_line : bool
        Whether to place each variable on a separate line

    Returns
    -------
    out : labeller
        Labelling function
    """
    if x is None:
        x = default

    if isinstance(x, labeller):
        return x

    x = _as_strip_labelling_func(x)
    return labeller(rows=x, cols=x, multi_line=multi_line)


class labeller:
    """
    Facet Strip Labelling

    When called with strip_label_details knows how to
    alter the strip labels along either dimension.

    Parameters
    ----------
    rows : str | callable
        How to label the rows
    cols : str | callable
        How to label the columns
    multi_line : bool
        Whether to place each variable on a separate line
    default : str | callable
        Fallback labelling function. If it is a string, it should be
        one of `["label_value", "label_both", "label_context"]`{.py}.
    kwargs : dict
        {variable name : function | string} pairs for
        renaming variables. A function to rename the variable
        or a string name.
    """

    def __init__(
        self,
        rows: Optional[CanBeStripLabellingFunc] = None,
        cols: Optional[CanBeStripLabellingFunc] = None,
        multi_line: bool = True,
        default: CanBeStripLabellingFunc = "label_value",
        **kwargs: Callable[[str], str],
    ):
        # Sort out the labellers along each dimension
        self.rows_labeller = _as_strip_labelling_func(rows, default)
        self.cols_labeller = _as_strip_labelling_func(cols, default)
        self.multi_line = multi_line
        self.variable_maps = kwargs

    def __call__(self, label_info: strip_label_details) -> strip_label_details:
        """
        Called to do the labelling
        """
        variable_maps = {
            k: v
            for k, v in self.variable_maps.items()
            if k in label_info.variables
        }

        # No variable specific labeller
        if label_info.meta["dimension"] == "rows":
            result = self.rows_labeller(label_info)
        else:
            result = self.cols_labeller(label_info)

        # Make dict_labeler for the  variable specific labelers
        # do the label and merge
        if variable_maps:
            d = {
                value: variable_maps[var]
                for var, value in label_info.variables.items()
                if var in variable_maps
            }
            func = _as_strip_labelling_func(d)
            result2 = func(label_info)
            result.variables.update(result2.variables)

        if not self.multi_line:
            result = result.collapse()

        return result


def _as_strip_labelling_func(
    fobj: Optional[CanBeStripLabellingFunc],
    default: CanBeStripLabellingFunc = "label_value",
) -> StripLabellingFunc:
    """
    Create a function that can operate on strip_label_details
    """
    if fobj is None:
        fobj = default

    if isinstance(fobj, str) and fobj in LABELLERS:
        return LABELLERS[fobj]

    if isinstance(fobj, _core_labeller):
        return fobj
    elif callable(fobj):
        if fobj.__name__ in LABELLERS:
            return fobj  # type: ignore
        else:
            return _function_labeller(fobj)  # type: ignore
    elif isinstance(fobj, dict):
        return _dict_labeller(fobj)
    else:
        msg = f"Could not create a labelling function for with `{fobj}`."
        raise PlotnineError(msg)


class _core_labeller(metaclass=ABCMeta):
    """
    Per item
    """

    @abstractmethod
    def __call__(self, label_info: strip_label_details) -> strip_label_details:
        pass


class _function_labeller(_core_labeller):
    """
    Use a function turn facet value into a label

    Parameters
    ----------
    func : callable
        Function to label an individual string
    """

    def __init__(self, func: Callable[[str], str]):
        self.func = func

    def __call__(self, label_info: strip_label_details) -> strip_label_details:
        label_info = label_info.copy()
        variables = label_info.variables
        for facet_var, facet_value in variables.items():
            variables[facet_var] = self.func(facet_value)
        return label_info


class _dict_labeller(_core_labeller):
    """
    Use a dict to alter specific facet values

    Parameters
    ----------
    lookup : dict
        A dict of the one of the forms
          - {facet_value: label_value}
          - {facet_value: callable(<label_value>)}
    """

    def __init__(
        self, lookup: dict[str, str] | dict[str, Callable[[str], str]]
    ):
        self.lookup = lookup

    def __call__(self, label_info: strip_label_details) -> strip_label_details:
        label_info = label_info.copy()
        variables = label_info.variables
        # Replace facet_value with values from the lookup table
        # If the value is function, call it  the result of calling function
        for facet_var, facet_value in variables.items():
            target = self.lookup.get(facet_value)
            if target is None:
                continue
            elif callable(target):
                variables[facet_var] = target(facet_value)
            else:
                variables[facet_var] = target
        return label_info
