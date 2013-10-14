from ggplot import *

ggplot(diamonds, aes(x='price', color='cut')) + \
    geom_density() + \
    facet_grid("cut", "color")

