from ggplot import *

print ggplot(diamonds, aes(x='price', color='cut')) + \
    geom_density() + \
    facet_grid("cut", "color")

plt.show(1)
