from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path
from subprocess import PIPE, Popen
from typing import Literal, Optional, Sequence, TypeAlias

TPL_FILENAME = "release-checklist-tpl.md"
THIS_DIR = Path(__file__).parent
NEW_ISSUE = "https://github.com/has2k1/plotnine/issues/new"

VersionPart: TypeAlias = Literal[
    "major",
    "minor",
    "patch",
]

count = r"(?:[0-9]|[1-9][0-9]+)"
DESCRIBE_PATTERN = re.compile(
    r"^v"
    rf"(?P<version>{count}\.{count}\.{count})"
    rf"(?P<pre>(a|b|rc){count})?"
    r"(-(?P<commits>\d+)-g(?P<hash>[a-z0-9]+))?"
    r"(?P<dirty>-dirty)?"
    r"$"
)


def run(cmd: str | Sequence[str], input: Optional[str] = None) -> str:
    """
    Run command
    """
    if isinstance(cmd, str) and os.name == "posix":
        cmd = shlex.split(cmd)
    with Popen(
        cmd, stdin=PIPE, stderr=PIPE, stdout=PIPE, text=True, encoding="utf-8"
    ) as p:
        stdout, _ = p.communicate(input=input)
    return stdout.strip()


def copy_to_clipboard(s: str):
    """
    Copy s to clipboard
    """
    import platform

    plat = platform.system()

    platform_cmds = {"Darwin": "pbcopy", "Linux": "xclip", "Windows": "clip"}

    try:
        from pandas.io import clipboard
    except ImportError:
        try:
            cmd = platform_cmds[plat]
        except KeyError as err:
            msg = f"No clipboard for this system: {plat}"
            raise RuntimeError(msg) from err
        run(cmd, input=s)
    else:
        clipboard.copy(s)  # type: ignore


def get_previous_version(s: Optional[str] = None) -> str:
    """
    Get previous version

    Either the 2nd commandline arg (v) or obtained from git describe
    """
    if s:
        vtxt = s if s.startswith("v") else f"v{s}"
    else:
        cmd = "git describe --dirty --tags --long --match '*[0-9]*'"
        vtxt = run(cmd)

    m = DESCRIBE_PATTERN.match(vtxt)
    if not m:
        raise ValueError(f"Bad version: {vtxt}")

    return m.group("version")


def bump_version(version: str, part: VersionPart) -> str:
    """
    Bump version
    """
    parts = version.split(".")
    i = ("major", "minor", "patch").index(part)
    parts[i] = str(int(parts[i]) + 1)
    # Zero-out the smaller parts
    for j in range(i + 1, 3):
        parts[j] = "0"
    return ".".join(parts)


def generate_checklist(version: str) -> str:
    """
    Generate checklist for releasing the given version
    """
    path = THIS_DIR / TPL_FILENAME
    pattern = re.compile(
        # The template is everything below the dashed line
        r"\n-+\n(?P<tpl>.+)",
        flags=re.MULTILINE | re.DOTALL,
    )
    with Path(path).open("r") as f:
        contents = f.read()

    m = pattern.search(contents)
    if not m:
        raise ValueError(f"Cannot find the relevant content in '{path}'")

    tpl = m.group("tpl")
    return tpl.replace("<VERSION>", version)


def process(part: VersionPart, prev: str | None):
    """
    Run the full process

    1. Calculate the next version from the previous version
    2. Add the next version to the checklist template
    3. Copy the template to the system clipboard
    """
    prev_version = get_previous_version(prev)
    next_version = bump_version(prev_version, part)
    cl = generate_checklist(next_version)
    copy_to_clipboard(cl)
    verbose(prev_version, next_version)


def verbose(prev_version, next_version):
    """
    Print version details
    """
    from textwrap import dedent

    from term import T0 as T  # type: ignore

    s = f"""
    Previous Version: {T(prev_version, "lightblue", effect="strikethrough")}
        Next Version: {T(next_version, "lightblue", effect="bold")}

    The release checklist has been copied to the clipboard. Use it to
    open a new issue at: {T(NEW_ISSUE, "yellow")}\
    """
    print(dedent(s))


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        part = sys.argv[1]
        prev = sys.argv[2] if len(sys.argv) >= 3 else None
        assert part in ("major", "minor", "patch")
        process(part, prev)
