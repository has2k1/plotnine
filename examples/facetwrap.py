from ggplot import *


print (ggplot(aes(x='price'), data=diamonds) + \
    geom_hist() + \
    facet_wrap("cut"))

plt.show(1)
