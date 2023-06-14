import numpy as np
import pandas as pd

from plotnine import (
    aes,
    annotate,
    geom_bar,
    geom_line,
    geom_point,
    ggplot,
    scale_color_gradientn,
    scale_fill_gradientn,
    theme,
    theme_void,
)

n = 99

x = np.linspace(0, 1, n)
y = np.exp(-7 * (x - 0.5) ** 2)

data = pd.DataFrame({"x": x, "y": y})

bcolor = "#9e2f68"
bcolor_lighter = "#f4d8e6"
bcolor_darker = "#631d41"

gradient = (
    (0.99, 0.88, 0.87),
    (0.98, 0.62, 0.71),
    (0.86, 0.20, 0.59),
    bcolor,
    bcolor,
    bcolor_darker,
    bcolor_darker,
)

data1 = data[: n // 3 : 9]
data2 = data[n // 3 : 2 * n // 3]
data3 = data[2 * n // 3 :: 12]

p = (
    ggplot(mapping=aes("x", "y", color="y", fill="y"))
    + annotate(
        geom="label",
        x=0.260,
        y=0.493,
        family="Helvetica",
        label="pl  tnine",
        label_size=1.5,
        label_padding=0.1,
        size=24,
        fill=bcolor_lighter,
        color=bcolor,
    )
    + geom_point(data=data1, size=8, stroke=0, show_legend=False)
    + geom_line(data=data2, size=2, color=bcolor_darker, show_legend=False)
    + geom_bar(aes("x+.06"), data3, stat="identity", size=0, show_legend=False)
    + scale_color_gradientn(colors=gradient)
    + scale_fill_gradientn(colors=gradient)
    + theme_void()
    + theme(figure_size=(3.6, 3.6))
)

p.save("logo.pdf")

# Remove the project name
p.layers = p.layers.__class__(p.layers[1:])
p.save("logo-small.pdf")
