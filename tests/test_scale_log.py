from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd

from ggplot import *

df = pd.DataFrame({"x": np.linspace(0, 10, 10),
                   "y": np.linspace(0, 3, 10),})

df['y'] = 10.**df.y

gg = ggplot(aes(x="x", y="y"), data=df) + geom_line()

print(gg)
print(gg + scale_y_log())
print(gg + scale_x_log())
print(gg + scale_x_log()+ scale_y_log())
print(gg + scale_x_log(2)+ scale_y_log(2))
