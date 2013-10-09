from ggplot import *


ggplot(aes(x='price'), data=diamonds) + \
    geom_hist() +
    facet_wrap("cut")
