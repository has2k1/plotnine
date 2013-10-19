from ggplot import *

print (ggplot(aes(x='date', y='beef'), data=meat) + \
    geom_line())

plt.show(1)
