from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from ggplot import *
c = ggplot(aes("qsec", "wt",label='name'), mtcars)
print(c + geom_point() + geom_text(aes(hjust = -0.1, vjust = 0.1)))
