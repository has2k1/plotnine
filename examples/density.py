from ggplot import *

print ggplot(diamonds, aes(x='price', color='cut')) + \
        geom_density()

plt.show(1)
