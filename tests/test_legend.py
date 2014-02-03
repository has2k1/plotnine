from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from ggplot import *

p = ggplot(mtcars, aes(x='qsec', y='mpg', color='cyl', size='hp')) + geom_point()
print(p)
plt.show(1)
