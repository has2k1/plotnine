from ggplot import *

ggplot(diamonds, aes(x='price', color='cut')) + \
        geom_density()
