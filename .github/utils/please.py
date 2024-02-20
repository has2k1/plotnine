import sys
from typing import Callable, TypeAlias

from _repo import Git

Ask: TypeAlias = Callable[[], bool | str]
Do: TypeAlias = Callable[[], str]


def can_i_deploy_documentation() -> bool:
    """
    Return True if documentation should be deployed
    """
    return (
        Git.is_release()
        or Git.is_pre_release()
        or Git.branch() in ("main", "dev")
    )


def where_can_i_deploy_documentation() -> str:
    """
    Return branch to deploy documentation to
    """
    if Git.is_release():
        return "website"
    elif Git.is_pre_release():
        return "pre-website"
    else:
        return "gh-pages"


def process_request(arg: str) -> str:
    if arg in REQUESTS:
        result = REQUESTS.get(arg, lambda: False)()
        if not isinstance(result, str):
            result = str(result).lower()
    else:
        result = ACTIONS.get(arg, lambda: "")()
    return result


REQUESTS: dict[str, Ask] = {
    "can_i_deploy_documentation": can_i_deploy_documentation,
    "where_can_i_deploy_documentation": where_can_i_deploy_documentation,
}


ACTIONS: dict[str, Do] = {}


if __name__ == "__main__":
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        print(process_request(arg))
