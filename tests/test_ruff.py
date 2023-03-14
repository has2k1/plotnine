import os
import subprocess
from pathlib import Path

# Helps contributors catch linter errors
# when they run make test.

if not os.environ.get("CI"):

    def test_ruff():
        plotnine_dir = str(Path(__file__).parent.parent.absolute())
        p = subprocess.Popen(
            ["ruff", plotnine_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Ignore the stderr msg as it is mostly noise
        # about coverage warnings
        stdout, _ = p.communicate()
        s = stdout.decode("utf-8")
        msg = f"rufff found the following issues: \n\n{s}"
        assert p.returncode == 0, msg
