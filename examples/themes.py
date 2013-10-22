from ggplot import *


p = ggplot(mtcars, aes('cyl')) + geom_bar()
print(p)
print(p +theme_bw())
print(p + theme_xkcd())
print(p + theme_matplotlib())
plt.show(1)
