from ggplot import *

print (ggplot(diamonds, aes(x='carat')) + \
    geom_histogram())

plt.show(1)
