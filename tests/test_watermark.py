from pathlib import Path

import pandas as pd

from plotnine import aes, geom_point, ggplot, watermark

wm_file = Path(__file__).parent / "images/plotnine-watermark.png"


def test_watermark():
    data = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})

    p = (
        ggplot(data)
        + geom_point(aes("x", "y"))
        + watermark(wm_file, 150, 160)
        + watermark(wm_file, 150, 210, 0.5)
    )

    assert p == "watermark"
