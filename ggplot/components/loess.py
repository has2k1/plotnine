from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
"""
loess(formula, data, weights, subset, na.action, model = FALSE,
      span = 0.75, enp.target, degree = 2,
      parametric = FALSE, drop.square = FALSE, normalize = TRUE,
      family = c("gaussian", "symmetric"),
      method = c("loess", "model.frame"),
      control = loess.control(...), ...)

a formula specifying the numeric response and one to four numeric predictors
(best specified via an interaction, but can also be specified additively).
Will be coerced to a formula if necessary.
"""
import pylab as pl
import pandas as pd
import numpy as np

def loess( x, h, xp, yp ):
    "loess func"

    """args:
        x => location
        h => bandwidth (not sure how to choose this automatically)
        xp => vector
        yp => vector

    example:
        X = np.arange(1, 501)
        y = np.random.random_integers(low=75, high=130, size=len(X))
        data = np.array(zip(X,y))

        s1, s2 = [], []

        for k in data[:,0]:
            s1.append( loess( k, 5, data[:,0], data[:,1] ) )
            s2.append( loess( k, 100, data[:,0], data[:,1] ) )

        pl.plot( data[:,0], data[:,1], 'o', color="white", markersize=1, linewidth=3 )
        pl.plot( data[:,0], np.array(s1), 'k-', data[:,0], np.array(s2), 'k--' )
        pl.show()
    """
    w = np.exp( -0.5*( ((x-xp)/h)**2 )/np.sqrt(2*np.pi*h**2) )
    b = sum(w*xp)*sum(w*yp) - sum(w)*sum(w*xp*yp)
    b /= sum(w*xp)**2 - sum(w)*sum(w*xp**2)
    a = ( sum(w*yp) - b*sum(w*xp) )/sum(w)
    return a + b*x




