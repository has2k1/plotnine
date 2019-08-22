import subprocess
import unittest
from pathlib import Path

file_dir = Path(__file__).parent


class Flake8TestCase(unittest.TestCase):
    def test_flake8(self):
        p = subprocess.Popen(
            ["flake8", str((file_dir.parent).absolute())],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            self.fail(
                "Flake 8 found issues: %s\n%s"
                % (stdout.decode("utf-8"), stderr.decode("utf-8"))
            )
