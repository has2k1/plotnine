#!/usr/bin/env python
#
# This updates the baseline images with:
#
#    1. failing test result images
#    2. result images without baseline images

from pathlib import Path
from typing import Generator

baseline = Path("tests/baseline_images/")
result = Path("tests/result_images/")


def new_test_images() -> Generator[Path, None, None]:
    """
    Get all test images that are failing or have no baseline
    """
    _exp, _fail = ("-expected.png", "-failed-diff.png")
    for d in result.iterdir():
        for png in d.glob("*.png"):
            if png.name.endswith(_exp) or png.name.endswith(_fail):
                continue

            expected = png.with_name(f"{png.stem}{_exp}")
            failed = png.with_name(f"{png.stem}{_fail}")

            if failed.exists() or not expected.exists():
                yield png


def baseline_path(new_test_image: Path) -> Path:
    """
    Convert a test result image path to a baseline image path
    """
    return baseline / "/".join(new_test_image.parts[2:])


def result_to_baseline():
    """
    Copy new or failing tests/result_images to tests/baseline_images
    """
    for image in new_test_images():
        new_baseline_image = baseline_path(image)
        new_baseline_image.parent.mkdir(parents=True, exist_ok=True)
        image.replace(new_baseline_image)


if __name__ == "__main__":
    result_to_baseline()
