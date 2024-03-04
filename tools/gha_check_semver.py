"""
Check the Tag on Github Actions

Writes the following variables to the output file for the github step:

    1. tag_type=<tag_type>
       Possible values are:
           - alpha
           - beta
           - candidate
           - final
           - ""

    2. publish_on=<publish_on>
       Possible values are:
           - pypi
           - testpypi
           - ""

The output of this script should tell you whether to publish a release
and to what index.
"""

import os
import re
from pathlib import Path
from typing import Literal, TypeAlias

TagType: TypeAlias = Literal[
    "alpha",
    "beta",
    "candidate",
    "final",
]


count = r"(?:[0-9]|[1-9][0-9]+)"
SEMVER_PATTERN = re.compile(
    r"^v"
    rf"(?P<version>{count}\.{count}\.{count})"
    rf"(?P<pre>(a|b|rc){count})?"
    r"$"
)


def get_tag_type() -> TagType | None:
    """
    Return the type of semantic version
    """
    tag = os.environ.get("GITHUB_REF_NAME")

    # Probably not on GHA
    if not tag:
        return

    m = SEMVER_PATTERN.match(tag)
    if not m:
        return

    pre = m.group("pre")

    if pre:
        if pre == "a":
            return "alpha"
        elif pre == "b":
            return "beta"
        else:
            return "candidate"

    return "final"


def output_tag_type(tag_type: TagType | None):
    """
    Write tag_type to the GHA output
    """
    if not (output_file := os.environ.get("GITHUB_OUTPUT")):
        return

    with Path(output_file).open("a") as f:
        print(f"tag_type={tag_type}", file=f)


def output_publish_on(tag_type: TagType | None):
    """
    Write index (pypi or testpypi) to publish on to the GHA output

    i.e. Where to release
    """
    if not (output_file := os.environ.get("GITHUB_OUTPUT")):
        return

    # Probably not on GHA
    if not output_file:
        return

    if tag_type in ("alpha", "beta", "candidate"):
        publish_on = "testpypi"
    elif tag_type == "final":
        publish_on = "pypi"
    else:
        publish_on = ""

    with Path(output_file).open("a") as f:
        print(f"publish_on={publish_on}", file=f)


if __name__ == "__main__":
    tag_type = get_tag_type()
    output_tag_type(tag_type)
    output_publish_on(tag_type)
