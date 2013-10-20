from ggplot import *


p = ggplot(aes(x='x', y='y'), data=diamonds)
print p + geom_point() + facet_grid("cut", "clarity", scales="free")
plt.show(1)
