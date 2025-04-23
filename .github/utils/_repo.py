#!/usr/bin/env python
from __future__ import annotations

import os
import re
import shlex
from subprocess import PIPE, Popen
from typing import Literal, Sequence, TypeAlias

ReleaseType: TypeAlias = Literal[
    "alpha",
    "beta",
    "candidate",
    "development",
    "stable",
]

pre_release_lookup: dict[str, ReleaseType] = {
    "a": "alpha",
    "alpha": "alpha",
    "b": "beta",
    "beta": "beta",
    "rc": "candidate",
    "dev": "development",
    ".dev": "development",
}

# https://docs.github.com/en/actions/learn-github-actions/variables
# #default-environment-variables
GITHUB_VARS = [
    "GITHUB_REF_NAME",  # main, dev, v0.1.0, v0.1.3a1
    "GITHUB_REF_TYPE",  # "branch" or "tag"
    "GITHUB_REPOSITORY",  # has2k1/scikit-misc
    "GITHUB_SERVER_URL",  # https://github.com
    "GITHUB_SHA",  # commit shasum
    "GITHUB_WORKSPACE",  # /home/runner/work/scikit-misc/scikit-misc
    "GITHUB_EVENT_NAME",  # push, schedule, workflow_dispatch, ...
]


count = r"(?:[0-9]|[1-9][0-9]+)"
DESCRIBE = re.compile(
    r"^v"
    rf"(?P<version>{count}\.{count}\.{count})"
    rf"((?P<pre>a|b|rc|alpha|beta|\.dev){count})?"
    r"(-(?P<commits>\d+)-g(?P<hash>[a-z0-9]+))?"
    r"(?P<dirty>-dirty)?"
    r"$"
)

# Define a stable release version to be valid according to PEP440
# and is a semver
STABLE_TAG = re.compile(r"^v" rf"{count}\.{count}\.{count}" r"$")

# Prerelease version
PRE_RELEASE_TAG = re.compile(
    r"^v"
    rf"{count}\.{count}\.{count}"
    rf"((?P<pre>a|b|rc|alpha|beta|\.dev){count})?"
    r"$"
)

REF_NAME = os.environ.get("GITHUB_REF_NAME", "")
REF_TYPE = os.environ.get("GITHUB_REF_TYPE", "")


def run(cmd: str | Sequence[str]) -> str:
    if isinstance(cmd, str) and os.name == "posix":
        cmd = shlex.split(cmd)
    with Popen(
        cmd, stdin=PIPE, stderr=PIPE, stdout=PIPE, text=True, encoding="utf-8"
    ) as p:
        stdout, _ = p.communicate()
    return stdout.strip()


class Git:
    @staticmethod
    def checkout(committish):
        """
        Return True if inside a git repo
        """
        res = run(f"git checkout {committish}")
        return res

    @staticmethod
    def commit_titles(n=1) -> list[str]:
        """
        Return a list n of commit titles
        """
        output = run(
            f"git log --oneline --no-merges --pretty='format:%s' -{n}"
        )
        return output.split("\n")[:n]

    @staticmethod
    def commit_messages(n=1) -> list[str]:
        """
        Return a list n of commit messages
        """
        sep = "______ MESSAGE _____"
        output = run(
            f"git log --no-merges --pretty='format:%B{sep}' -{n}"
        ).strip()
        if output.endswith(sep):
            output = output[: -len(sep)]
        return output.split(sep)[:n]

    @staticmethod
    def commit_title() -> str:
        """
        Commit subject
        """
        return Git.commit_titles(1)[0]

    @staticmethod
    def commit_message() -> str:
        """
        Commit title
        """
        return Git.commit_messages(1)[0]

    @staticmethod
    def is_repo():
        """
        Return True if inside a git repo
        """
        res = run("git rev-parse --is-inside-work-tree")
        return res == "return"

    @staticmethod
    def fetch_tags() -> str:
        """
        Fetch all tags
        """
        return run("git fetch --tags --force")

    @staticmethod
    def is_shallow() -> bool:
        """
        Return True if current repo is shallow
        """
        res = run("git rev-parse --is-shallow-repository")
        return res == "true"

    @staticmethod
    def deepen(n: int = 1) -> str:
        """
        Fetch n commits beyond the shallow limit
        """
        return run(f"git fetch --deepen={n}")

    @staticmethod
    def describe() -> str:
        """
        Git describe to determine version
        """
        return run("git describe --dirty --tags --long --match '*[0-9]*'")

    @staticmethod
    def can_describe() -> bool:
        """
        Return True if repo can be "described" from a semver tag
        """
        return bool(DESCRIBE.match(Git.describe()))

    @staticmethod
    def get_tag_at_commit(committish: str) -> str:
        """
        Get tag of a given commit
        """
        return run(f"git describe --exact-match {committish}")

    @staticmethod
    def tag_message(tag: str) -> str:
        """
        Get the message of a tag
        """
        return run(f"git tag -l --format='%(subject)' {tag}")

    @staticmethod
    def is_annotated(tag: str) -> bool:
        """
        Return true if tag is annotated tag
        """
        # LHS prints to stderr and returns nothing when
        # tag is an empty string
        return run(f"git cat-file -t {tag}") == "tag"

    @staticmethod
    def shallow_checkout(branch: str, url: str, depth: int = 1) -> str:
        """
        Shallow clone upto n commits
        """
        _branch = f"--branch={branch}"
        _depth = f"--depth={depth}"
        return run(f"git clone {_depth} {_branch} {url} .")

    @staticmethod
    def is_stable_release():
        """
        Return True if event is a stable release
        """
        return REF_TYPE == "tag" and bool(STABLE_TAG.match(REF_NAME))

    @staticmethod
    def is_pre_release():
        """
        Return True if event is any kind of pre-release
        """
        return REF_TYPE == "tag" and bool(PRE_RELEASE_TAG.match(REF_NAME))

    @staticmethod
    def release_type() -> ReleaseType | None:
        if Git.is_stable_release():
            return "stable"
        elif Git.is_pre_release():
            match = PRE_RELEASE_TAG.match(REF_NAME)
            assert match is not None
            pre = match.group("pre")
            return pre_release_lookup[pre]

    @staticmethod
    def branch():
        """
        Return event branch
        """
        return REF_NAME if REF_TYPE == "branch" else ""
