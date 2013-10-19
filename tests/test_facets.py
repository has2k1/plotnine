from ggplot import *


p = ggplot(aes(x='x', y='y'), data=diamonds.head(1000))
print p + geom_point() + facet_wrap("cut", scales="free")
print p + geom_point() + facet_wrap("cut", nrow=2)
print p + geom_point() + facet_wrap("cut", ncol=3)
print p + geom_point() + facet_wrap("cut")

p = ggplot(aes(x='x', y='y'), data=diamonds)
print p + geom_point() + facet_grid("cut", "clarity", nrow=5, ncol=8)
print p + geom_point() + facet_grid("cut", "clarity", nrow=5)
print p + geom_point() + facet_grid("cut", "clarity",  ncol=5)
print p + geom_point() + facet_grid("cut", "clarity", scales="free")
