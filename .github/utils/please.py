import os
import sys
from pathlib import Path
from typing import Callable, TypeAlias

from _repo import Git

Ask: TypeAlias = Callable[[], bool | str]
Do: TypeAlias = Callable[[], str]

gh_output_file = os.environ.get("GITHUB_OUTPUT")


def set_deploy_to():
    """
    Write where to deploy to deploy_on in the GITHUB_OUTPUT env
    """
    if not gh_output_file:
        return

    if Git.is_stable_release():
        deploy_to = "website"
    elif Git.is_pre_release():
        deploy_to = "pre-website"
    elif Git.branch() in {"main", "dev"}:
        deploy_to = "gh-pages"
    else:
        deploy_to = ""

    with Path(gh_output_file).open("a") as f:
        print(f"deploy_to={deploy_to}", file=f)


def set_publish_on():
    """
    Write index (pypi or testpypi) to publish_on in the GITHUB_OUTPUT env

    i.e. Where to release
    """
    # Probably not on GHA
    if not gh_output_file:
        return

    rtype = Git.release_type()

    if rtype in {"stable", "alpha", "beta", "development"}:
        publish_on = "pypi"
    elif rtype == "candidate":
        publish_on = "testpypi"
    else:
        publish_on = ""

    with Path(gh_output_file).open("a") as f:
        print(f"publish_on={publish_on}", file=f)


def set_commit_title():
    """
    Write the commit title to commit_title in the GITHUB_OUTPUT env
    """
    if not gh_output_file:
        return

    with Path(gh_output_file).open("a") as f:
        print(f"commit_title={Git.commit_title()}", file=f)


def process_request(task_name: str) -> str | None:
    if task_name in TASKS:
        return TASKS[task_name]()


TASKS: dict[str, Callable[[], str | None]] = {
    "set_deploy_to": set_deploy_to,
    "set_publish_on": set_publish_on,
    "set_commit_title": set_commit_title,
}

if __name__ == "__main__":
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        output = process_request(arg)
        if output:
            print(output)
