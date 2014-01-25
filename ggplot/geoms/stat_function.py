import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from .geom import geom
import pandas as pd
import numpy as np
import scipy.stats as stats

class stat_function(geom):
    """
    Superimpose a function onto a plot

    Uses a 

    Parameters
    ----------
    x : list, 1darray
        x values of data
    fun : function
        Function to draw.
    n : int
        Number of points to interpolate over. Must be greater than zero.
        Defaults to 101.
    color : str
        Color to draw function with.
    args : list, dict, object
        List or dict of additional arguments to pass to function. If neither
        list or dict, object is passed as second argument.
        

    Examples
    --------

    Sin vs cos.
    
    .. plot::
        :include-source:
    
        import numpy as np
        import pandas as pd
        from ggplot import *
        gg = ggplot(pd.DataFrame({'x':np.arange(10)}),aes(x='x'))
        gg = gg + stat_function(fun=np.sin,color="red")
        gg = gg + stat_function(fun=np.cos,color="blue")
        print(gg)
        

    Compare random sample density to normal distribution.
    
    .. plot::
        :include-source:
        
        import numpy as np
        import pandas as pd
        from ggplot import *
        x = np.random.normal(size=100)
        # normal distribution function
        def dnorm(n): 
            return (1.0 / np.sqrt(2 * np.pi)) * (np.e ** (-0.5 * (n ** 2)))
        data = pd.DataFrame({'x':x})
        gg = ggplot(aes(x='x'),data=data) + geom_density()
        gg = gg + stat_function(fun=dnorm,n=150)
        print(gg)

    Passing additional arguments to function as list.
    
    .. plot::
        :include-source:
        
        import numpy as np
        import pandas as pd
        from ggplot import *
        x = np.random.randn(100)
        to_the_power_of = lambda n, p: n ** p
        y = x ** 3
        y += np.random.randn(100) # add noise
        data = pd.DataFrame({'x':x,'y':y})
        gg = ggplot(aes(x='x',y='y'),data=data) + geom_point()
        gg = gg + stat_function(fun=to_the_power_of,args=[3])
        print(gg)

    Passing additional arguments to function as dict.
    
    .. plot::
        :include-source:

        import scipy
        import numpy as np
        import pandas as pd
        from ggplot import *        
        def dnorm(x, mean, var): 
            return scipy.stats.norm(mean,var).pdf(x)
        data = pd.DataFrame({'x':np.arange(-5,6)})
        gg = ggplot(aes(x='x'),data=data)
        gg = gg + stat_function(fun=dnorm,color="blue",args={'mean':0.0,'var':0.2})
        gg = gg + stat_function(fun=dnorm,color="red",args={'mean':0.0,'var':1.0})
        gg = gg + stat_function(fun=dnorm,color="yellow",args={'mean':0.0,'var':5.0})
        gg = gg + stat_function(fun=dnorm,color="green",args={'mean':-2.0,'var':0.5})
        print(gg)
    
    """
    VALID_AES = ['x','fun','n','color','args']
    REQUIRED_AES = ['x','fun']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        miss_aes = [aes for aes in self.REQUIRED_AES if aes not in layer]
        if(miss_aes):
            raise Exception("stat_function requires the following " +
                            "missing aesthetics: %s" % ", ".join(miss_aes))
        x = layer.pop('x')
        fun = layer.pop('fun')

        if 'args' in layer:
            args = layer.pop('args')
            old_fun = fun
            if isinstance(args,list):
                fun = lambda x: old_fun(x,*args)
            elif isinstance(args,dict):
                fun = lambda x: old_fun(x,**args)
            else:
                fun = lambda x: olf_fun(x,args)

        color = None if 'color' not in layer else layer.pop('color')
        n = 101 if 'n' not in layer else layer.pop('n')

        x_min = min(x)
        x_max = max(x)
        x_values = np.linspace(x_min,x_max,n)
        y_values = map(fun,x_values)

        if color:
            plt.plot(x_values,y_values,color=color)
        else:
            plt.plot(x_values,y_values)
