from ggplot import *


ggplot(aes(x='date', y='beef'), data=meat) + \
    stat_smooth()
