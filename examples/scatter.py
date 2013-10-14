from ggplot import *


print ggplot(aes(x='date', y='beef'), data=meat) + \
    geom_point()

plt.show(1)
