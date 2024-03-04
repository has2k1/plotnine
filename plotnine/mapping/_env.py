from __future__ import annotations

from collections.abc import MutableMapping
from contextlib import suppress
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any, Hashable, Protocol, Self

    class SupportsGetItem(Protocol):
        """
        Supports __getitem__
        """

        def __getitem__(self, key: str, /) -> Any: ...

        def __iter__(self) -> Iterator[Hashable]: ...


__all__ = ("Environment",)


@dataclass
class Environment:
    """
    A Python execution environment.

    Encapsulates a namespace for variable lookup
    """

    namespaces: list[SupportsGetItem]

    def __post_init__(self):
        self.namespace = StackedLookup(self.namespaces)
        """Where to look up variables from the encapsulated environment"""

    def with_outer_namespace(self, outer_namespace):
        """
        Return a new Environment with an extra namespace added.

        This namespace will be used only for variables that are not found
        in any existing namespace, i.e., it is "outside" them all.
        """
        return Environment(self.namespaces + [outer_namespace])

    def eval(self, expr: str, inner_namespace: SupportsGetItem = {}):
        """
        Evaluate some Python code in the encapsulated environment.

        Parameters
        ----------

        expr :
            A string containing a Python expression.

        inner_namespace :
            A dict-like object that will be checked first when `expr` attempts
            to access any variables.

        Returns
        -------
        :
            The value of `expr`.
        """
        code = _compile_eval(expr)
        return eval(
            code, {}, StackedLookup([inner_namespace] + self.namespaces)
        )

    @classmethod
    def capture(cls, eval_env: int | Self = 0):
        """
        Capture an execution environment from the stack.

        Parameters
        ----------
        eval_env :
            If `eval_env` is already an `Environment`, it is
            returned unchanged.

            Otherwise, we walk up the stack by `eval_env` steps and capture
            that function's evaluation environment.

        """
        import inspect

        if isinstance(eval_env, Environment):
            return eval_env

        frame = inspect.currentframe()
        frame_msg = "call-stack is not that deep!"
        if frame is None:
            raise ValueError(frame_msg)

        try:
            for i in range(eval_env + 1):
                frame = frame.f_back
                if frame is None:
                    raise ValueError(frame_msg)
            return cls([frame.f_locals, frame.f_globals])

        # The try/finally is important to avoid a potential reference cycle --
        # any exception traceback will carry a reference to *our* frame, which
        # contains a reference to our local variables, which would otherwise
        # carry a reference to some parent frame, where the exception was
        # caught...:
        finally:
            del frame

    def _namespace_ids(self):
        return [id(n) for n in self.namespaces]

    def __eq__(self, other):
        return (
            isinstance(other, Environment)
            and self._namespace_ids() == other._namespace_ids()
        )

    def __hash__(self):
        return hash((Environment, tuple(self._namespace_ids())))

    def __getstate__(*args, **kwargs):
        """
        Return state with no namespaces
        """
        return {"namespaces": [], "namespace": StackedLookup([])}

    def __deepcopy__(self, memo: dict[Any, Any]) -> Environment:
        """
        Shallow copy
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        for key, item in old.items():
            new[key] = item
            memo[id(new[key])] = new[key]

        return result


@dataclass
class StackedLookup(MutableMapping):
    """
    Iterative lookup in a stack of dicts

    Assignments go into an internal dict that is also the first place
    where a lookup is done.
    """

    stack: list[SupportsGetItem]

    def __post_init__(self):
        self._dict = {}
        self.stack = [self._dict] + list(self.stack)

    def __getitem__(self, key):
        for d in self.stack:
            with suppress(KeyError):
                return d[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __contains__(self, key):
        with suppress(KeyError):
            self[key]
            return True
        return False

    def __iter__(self):
        """
        Unique keys in stacking order
        """
        return iter({key: None for d in self.stack for key in d})

    def __len__(self):
        """
        Number of unique keys
        """
        return len({key for d in self.stack for key in d})

    def get(self, key: str, default: Any = None) -> Any:
        with suppress(KeyError):
            return self[key]
        return default

    def __repr__(self):
        return f"{self.__class__.__name__}({self.stack})"

    def __getstate__(*args, **kwargs):
        """
        Return state with no namespace
        """
        d = {}
        return {"stack": [d], "_dict": d}

    def copy(self):
        return self

    def __deepcopy__(self, memo: dict[Any, Any]) -> StackedLookup:
        """
        Shallow copy
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        for key, item in old.items():
            new[key] = item
            memo[id(new[key])] = new[key]

        return result


@lru_cache(maxsize=256)
def _compile_eval(source):
    """
    Cached compile in eval mode
    """
    return compile(source, "<string-expression>", "eval")
