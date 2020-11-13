import os
import subprocess
from pathlib import Path


if not os.environ.get('CI') and os.environ.get('TRAVIS'):
    def test_flake8():
        plotnine_dir = str(Path(__file__).parent.parent.absolute())
        p = subprocess.Popen(
            ['flake8', plotnine_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Ignore the stderr msg as it is mostly noise
        # about coverage warnings
        stdout, _ = p.communicate()
        msg = "flake8 found the following issues: \n\n{}".format(
                 stdout.decode('utf-8')
        )
        assert p.returncode == 0, msg
