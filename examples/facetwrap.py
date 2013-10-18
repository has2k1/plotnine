from ggplot import *


print ggplot(aes(x='price'), data=diamonds) + \
    geom_histogram() + \
    facet_wrap("cut")

plt.show(1)
