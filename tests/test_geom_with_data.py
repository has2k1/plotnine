from ggplot import *
gg = ggplot(mtcars, aes("wt", "mpg")) + geom_point()
g2 = gg + geom_text(aes(label="name"), data=mtcars[mtcars.cyl == 6])
g2.draw()
#print(g2)