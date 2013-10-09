from ggplot import *

p = ggplot(mtcars, aes('cyl'))
p + geom_bar()

