from ggplot import *


print ggplot(aes(x='date', y='beef'), data=meat) + \
    geom_point(alpha=0.3) + \
    stat_smooth(colour="black", se=True)

plt.show(1)
