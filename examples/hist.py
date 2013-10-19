from ggplot import *

print (ggplot(diamonds, aes(x='carat')) + \
    geom_hist())

plt.show(1)
