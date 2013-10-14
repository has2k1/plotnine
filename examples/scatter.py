from ggplot import *


ggplot(aes(x='date', y='beef'), data=meat) + \
    geom_point()
