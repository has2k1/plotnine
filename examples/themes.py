from ggplot import *


p = ggplot(mtcars, aes('cyl')) + geom_bar()
print "default theme"
print(p)
plt.show(1)
print "theme_bw()"
print(p +theme_bw())
plt.show(1)
print "theme_xkcd()"
print(p + theme_xkcd())
plt.show(1)
print "theme_matplotlib()"
print(p + theme_matplotlib())
plt.show(1)
