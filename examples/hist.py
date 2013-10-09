from ggplot import *

ggplot(diamonds, aes(x='carat')) + \
    geom_hist()

