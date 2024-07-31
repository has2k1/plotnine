import os
import subprocess
from pathlib import Path

import pytest

# Helps contributors catch linter errors
# when they run make test.

is_CI = os.environ.get("CI") is not None


@pytest.mark.skipif(is_CI, reason="Helps contributors catch linter errors")
def test_lint():
    plotnine_dir = str(Path(__file__).parent.parent.absolute())
    p = subprocess.Popen(
        ["ruff", "check", plotnine_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Ignore the stderr msg as it is mostly noise
    # about coverage warnings
    stdout, _ = p.communicate()
    s = stdout.decode("utf-8")
    msg = f"Linting test found the following issues: \n\n{s}"
    assert p.returncode == 0, msg


@pytest.mark.skipif(is_CI, reason="Helps contributors catch linter errors")
def test_format():
    plotnine_dir = str(Path(__file__).parent.parent.absolute())
    p = subprocess.Popen(
        ["ruff", "format", plotnine_dir, "--check"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Ignore the stderr msg as it is mostly noise
    # about coverage warnings
    _, stderr = p.communicate()
    s = stderr.decode("utf-8")
    msg = f"Formatting test found the following issues: \n\n{s}"
    assert p.returncode == 0, msg
