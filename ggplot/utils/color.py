"""
Python module for color functions.

"""

from __future__ import division
from __future__ import print_function
from __future__ import with_statement

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import types
from functools import partial

from collections import Iterable
from matplotlib.cbook import is_string_like
from matplotlib.cm import get_cmap
from matplotlib.colors import LinearSegmentedColormap


def display_color(c):
    """
    Utility for displaying a color. display_color will make a plot with a circle
    that is the input parameter.

    Parameters
    ==========
    c - string
        a color; can be RGB, hex, name, whatever
    """
    dot = plt.Circle((.5,.5), .4, color=c)
    fig = plt.gcf()
    fig.gca().add_artist(dot)
    plt.show()

def display_colors(cs):
    n = len(cs)
    fig = plt.gcf()
    print("Colors:")
    for i, c in enumerate(cs):
        print(i, c, (i, 0.5), 1./n)
        fig.gca().add_artist(plt.Circle((i/n, 0.5), 1./n, color=c))
    plt.show()

class SMeta(type):
    """
    Usage:
    __metaclass__ = SMeta
    """
    def __call__(*args):
        cls = args[0]
        key = args[1:]
        try:
            cache = cls._cache
        except:
            cache = dict()
            cls._cache = cache
        try:
            obj = cache[key]
        except:
            obj = type.__call__(*args)
            cache[key] = obj
        return obj

class ColorModel(object):
    """
    Color Model base class.
    Note that this is generated as "singleton" - only one object of each class.
    """
    __metaclass__ = SMeta
    limits =  np.tile(np.array([0.,1.]),(3,1))
    range = limits.copy()
    @classmethod
    def _inverse(self):
        raise NotImplementedError()
    @classmethod
    def inverse(cls, *args, **kwargs):
        """
        Return inverse color transform.

        Subclasses to define method _inverse to return instance of
        inverse object.
        """
        if len(args) > 0 or len(kwargs) > 0:
            return cls._inverse()(*args, **kwargs)
        return cls._inverse()
    def __call__(self, *agrs, **kwargs):
        """
        Accepts and return [x,3] array.
        Optionally deal with 3 vectors, 3 scalars.
        Treatment of 3x3 is ambiguous and will be interpreted as [x,3].
        """
        raise NotImplementedError()

    # a set of conversion routines to be used by derived classes
    @staticmethod
    def _args_to_vectors(args):
        """
        TODO - need to add auto-convert to gray
        """
        assert len(args) in (1,3)
        if len(args) == 3:
            if not isinstance(args[0], np.ndarray):
                mode = 0
                p0 = np.array([args[0]])
                p1 = np.array([args[1]])
                p2 = np.array([args[2]])
            else:
                mode = 1
                p0, p1, p2 = args
        else:
            arg = args[0]
            if isinstance(arg, Iterable) and not isinstance(arg, np.ndarray):
                arg = np.array(arg, dtype = np.float64)
            assert isinstance(arg, np.ndarray)
            if len(arg.shape) == 2:
                if arg.shape[1] == 3:
                    mode = 2
                    p0, p1, p2 = arg.transpose()
                else:
                    mode = 3
                    p0, p1, p2 = arg
            else:
                assert arg.shape == (3,)
                mode = 4
                p0, p1, p2 = arg[:,np.newaxis]
        return p0, p1, p2, mode
    @staticmethod
    def _args_to_array(args):
        """
        TODO - need to add auto-convert to gray
        """
        assert len(args) in (1,3)
        if len(args) == 3:
            if not isinstance(args[0], np.ndarray):
                mode = 0
                a = np.array([args])
            else:
                mode = 1
                a = np.array(args).transpose()
        else:
            arg = args[0]
            if isinstance(arg, Iterable) and not isinstance(arg, np.ndarray):
                arg = np.array(arg, dtype = np.float64)
            assert isinstance(arg, np.ndarray)
            if len(arg.shape) == 2:
                if arg.shape[1] == 3:
                    mode = 2
                    a = arg
                else:
                    mode = 3
                    a = arg.transpose()
            else:
                assert arg.shape == (3,)
                mode = 4
                a = np.array(args)
        return a, mode
    @staticmethod
    def _vectors_to_return(p0, p1, p2, mode):
        if mode == 0:
            return p0[0], p1[0], p2[0]
        if mode == 1:
            return p0, p1, p2
        if mode == 2:
            return np.vstack((p0, p1, p2)).transpose()
        if mode == 3:
            return np.vstack((p0, p1, p2))
        return np.hstack((p0, p1, p2))
    @staticmethod
    def _array_to_return(a, mode):
        if mode == 0:
            return a[0][0], a[0][1], a[0][2]
        if mode == 1:
            return a[:,0], a[:,1], a[:,2]
        if mode == 2:
            return a
        if mode == 3:
            return a.transpose()
        return a[0]
    
    # deal with gray values
    @staticmethod
    def _gray_args_to_vector(*args):
        assert len(args) == 1
        arg = args[0]
        if isinstance(arg, Iterable) and not isinstance(arg, np.ndarray):
            arg = np.array(arg, dtype = np.float64)
        if not isinstance(arg, np.ndarray):
            a = np.array(args)
            mode = 0
        else:
            if arg.shape == ():
                a = arg[np.newaxis]
                mode = 4
            elif len(arg.shape) == 1:
                mode = 2
                a = arg
            else:
                assert len(arg.shape) == 2
                if arg.shape[0] == 1:
                    mode = 2
                    a = arg[0,:]
                else:
                    assert arg.shape[1] == 1
                    mode = 3
                    a = arg[:,0]
        return a, mode
    @staticmethod
    def _gray_array_to_return(a, mode):
        if mode == 0:
            return a[0][0], a[0][1], a[0][2]
        if mode == 1:
            return a[:,0], a[:,1], a[:,2]
        if mode == 2:
            return a
        if mode == 3:
            return a.transpose()
        return a[0]

    @classmethod
    def gray(cls, *args):
        """
        Return gray value for given scalar in the source color space.

        Return should be:
        scalar --> tuple
        np_array --> np_array:
            [1,x] --> [3,x] for x > 1
            else:     [x,3]

        This is implemented in 
            cls._gray_array_to_return 

        Here we provide as default the method for RGB as this is used
        in all of the 'inverse' transforms.

        If a class provides arrays _gray_index and _gray_value
        then additionally we set in, e.g., [x, 3]
        [x,_gray_index] = [_gray_value]
        Typical use is a 2-vector, e.g., 
            _gray_index = [1,2]
            _gray_value = [0,1]
        for use in color circle values like HSV.    
        """
        v, mode = cls._gray_args_to_vector(*args)        
        a = np.tile(v,(3,1)).transpose()
        try:
            a[:,np.array(cls._gray_index)] = np.array(cls._gray_value)[np.newaxis,:]
        except:
            pass                
        return cls._array_to_return(a, mode)

    @classmethod
    def is_normal(cls, limits):
        """
        Check whether range is valid or should be normalized.

        This just covers a set of default checks from my old IDL
        routines.
        """
        for i in xrange(3):
            if cls.limits[i,1] > 1 and limits[i,1] <= 1:
                return False
            if cls.limits[i,1] <= 1 and limits[i,1] > cls.limits[i,1]:
                return False
            if cls.limits[i,0] > 1 and limits[i,0] < cls.limits[i,0]:
                return False
        return True
    @classmethod
    def normalize(cls, *args):
        """
        By default we just scale 0...1 range to limits no matter what
        the values.
        """
        a, mode = cls._args_to_array(*args)
        m = cls.limits[:,0][np.newaxis,:]
        M = cls.limits[:,1][np.newaxis,:]
        a = m + a*(M-m)
        print("why do we normalize?")
        return cls._array_to_return(a, mode)

class ColorModelMatrix(ColorModel):
    """
    Prototype for matric color classes.
    
    provides __call__ method
    requires _matrix class attribute
    """
    @classmethod
    def _transform(cls, a):
        return np.inner(a, cls._matrix)
    @classmethod        
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        a, mode = cls._args_to_array(args)
        np.clip(a, 
                (cls.limits[:,0])[np.newaxis,:], 
                (cls.limits[:,1])[np.newaxis,:],
                out = a)
        a = cls._transform(a)
        np.clip(a, 
                (cls.range[:,0])[np.newaxis,:], 
                (cls.range[:,1])[np.newaxis,:], 
                out = a)
        return cls._array_to_return(a, mode)

#######################################################################
# define specific color models

class ColorRGB(ColorModel):
    """
    RGB is essentially just identity.
    """
    @classmethod
    def _inverse(cls):
        return cls()
    @classmethod
    def __call__(cls, *args): 
        __doc__ = ColorModel.__call__.__doc__
        return cls._array_to_return(*cls._args_to_array(*args))

#-----------------------------------------------------------------------

class ColorCMY(ColorRGB):
    """
    Convert CMY to RGB or inverse.
    """
    @classmethod
    def __call__(cls, *args): 
        __doc__ = ColorModel.__call__.__doc__
        cmy, mode = cls._args_to_array(*args)
        rgb = 1 - cmy
        return cls._array_to_return(rgb, mode)

#-----------------------------------------------------------------------

class ColorHSV(ColorModel):
    """
    HSV color model.

    hue = [0, 360]
    saturation = [0, 1]
    value =[0, 1]
    """
    limits = np.array([[0., 360.],[0., 1.],[0., 1.]])
    _perm = np.array([[0,1,2],[1,0,2],[2,0,1],[2,1,0],[1,2,0],[0,2,1]])
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        h, s, v, mode = cls._args_to_vectors(args)
        np.mod(h, 360., out = h)
        np.clip(s,0,1, out = s)
        np.clip(v,0,1, out = v)
        c = v * s
        p = h / 60.
        x = c * (1 - np.abs(np.mod(p, 2.) - 1.))
        m = v - c
        z = np.zeros_like(x)
        col = np.vstack((c,x,z)).transpose()        
        ip = np.int64(p)
        rgb = col[np.tile(np.arange(len(x)),(3,1)).transpose(),cls._perm[ip]]
        rgb += m[:,np.newaxis]
        np.clip(rgb,0,1, out = rgb)
        return cls._array_to_return(rgb, mode)
    @classmethod
    def _inverse(cls, *args, **kwargs):
        return ColorHSVInverse()
    _gray_index = [0,1]
    _gray_value = [90,0]

class ColorHSVInverse(ColorModel):
    """
    Convert RGB to HSV.
    """
    range = ColorHSV.limits
    @classmethod
    def __call__(cls, *args):
        """
        Convert colors.

        Return:
          hue = [0, 360]
          saturation = [0, 1]
          value =[0, 1]
        """
        r, g, b, mode = cls._args_to_vectors(args)        
        M = np.maximum(r,np.maximum(g,b))
        m = np.minimum(r,np.minimum(g,b))
        C = M - m
        h = np.zeros_like(C)
        i = M == r
        h[i] = np.mod((g[i]-b[i])/C[i],6)
        i  = M == g
        h[i] = (b[i]-r[i])/C[i] + 2 
        i = M == b
        h[i] = (r[i]-g[i])/C[i] + 4
        H = h * 60
        V = M
        S = np.zeros_like(C)
        i = C != 0
        S[i] = C[i]/V[i]
        return cls._vectors_to_return(H,S,V, mode)
    @staticmethod
    def _inverse():
        return ColorHSV()

#-----------------------------------------------------------------------

class ColorHSL(ColorModel):
    """
    HSL color model.

    hue = [0, 360]
    saturation = [0, 1]
    lightness =[0, 1]
    """
    limits = np.array([[0., 360.],[0., 1.],[0., 1.]])
    _perm = np.array([[0,1,2],[1,0,2],[2,0,1],[2,1,0],[1,2,0],[0,2,1]])
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        h, s, l, mode = cls._args_to_vectors(args)
        np.mod(h, 360., out = h)
        np.clip(s,0,1, out = s)
        np.clip(l,0,1, out = l)
        c = (1 - np.abs(2 * l - 1)) * s
        p = h / 60.
        x = c * (1 - np.abs(np.mod(p, 2.) - 1.))
        m = l - 0.5 * c
        z = np.zeros_like(x)
        col = np.vstack((c,x,z)).transpose()        
        ip = np.int64(p)
        rgb = col[np.tile(np.arange(len(x)),(3,1)).transpose(),cls._perm[ip]]
        rgb += m[:,np.newaxis]
        np.clip(rgb,0,1, out = rgb)
        return cls._array_to_return(rgb, mode)
    @staticmethod
    def _inverse():
        return ColorHSLInverse()
    _gray_index = [0,1]
    _gray_value = [90,0.]

class ColorHSLInverse(ColorModel):
    """
    Convert RGB to HSL.
    """
    range = ColorHSL.limits
    @classmethod
    def __call__(cls, *args):
        """
        Convert colors.

        Return:
          hue = [0, 360]
          lightness = [0, 1]
          saturation = [0, 1]
        """
        r, g, b, mode = cls._args_to_vectors(args)        
        M = np.maximum(r,np.maximum(g,b))
        m = np.minimum(r,np.minimum(g,b))
        C = M - m
        h = np.zeros_like(C)
        i = M == r
        h[i] = np.mod((g[i]-b[i])/C[i],6)
        i  = M == g
        h[i] = (b[i]-r[i])/C[i] + 2 
        i = M == b
        h[i] = (r[i]-g[i])/C[i] + 4
        H = h * 60
        L = 0.5*(M + m)
        S = np.zeros_like(C)
        i = C != 0
        S[i] = C[i] / V(1 - np.abs(2 * L[i]-1)) 
        return cls._vectors_to_return(H,S,L, mode)
    @staticmethod
    def _inverse():
        return ColorHSL()

#-----------------------------------------------------------------------

class ColorHSI(ColorModel):
    """
    HSI color model.

    hue = [0, 360]
    saturation = [0, 1]
    intensity =[0, 1]
    """
    limits = np.array([[0., 360.],[0., 1.],[0., 1.]])
    _perm = np.array([[0,1,2],[2,0,1],[1,2,0]])
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        h, s, i, mode = cls._args_to_vectors(args)
        np.mod(h, 360., out = h)
        np.clip(i,0,1, out = i)
        np.clip(s,0,1, out = s)
        p = h / 60.
        f = 0.5 * np.mod(p, 2.)
        c = s * i * 3
        x = c * (1 - f)
        y = c * f
        z = np.zeros_like(x)
        m = i - i * s
        col = np.vstack((x,y,z)).transpose()        
        ip = np.int64(p/2)
        rgb = col[np.tile(np.arange(len(x)),(3,1)).transpose(),cls._perm[ip]]
        rgb += m[:,np.newaxis]
        np.clip(rgb,0,1, out = rgb)
        return cls._array_to_return(rgb, mode)
    @staticmethod
    def _inverse():
        return ColorHSIInverse()
    _gray_index = [0,1]
    _gray_value = [90,0.]

class ColorHSIInverse(ColorModel):
    """
    Convert RGB to HSI.
    """
    range = ColorHSI.limits
    @classmethod
    def __call__(cls, *args):
        """
        Convert colors.

        Return:
          hue = [0, 360]
          lightness = [0, 1]
          saturation = [0, 1]
        """
        r, g, b, mode = cls._args_to_vectors(args)
        r = clip(r,1,0)
        g = clip(g,1,0)
        b = clip(b,1,0)        
        M = np.maximum(r,np.maximum(g,b))
        m = np.minimum(r,np.minimum(g,b))
        C = M - m
        h = np.zeros_like(C)
        i = M == r
        h[i] = np.mod((g[i]-b[i])/C[i],6)
        i  = M == g
        h[i] = (b[i]-r[i])/C[i] + 2 
        i = M == b
        h[i] = (r[i]-g[i])/C[i] + 4
        H = h * 60
        I = (r + g + b) / 3.
        S = np.zeros_like(C)
        i = C != 0
        S[i] = 1 - m[i] / I[i]
        return cls._vectors_to_return(H,S,I, mode)
    @staticmethod
    def _inverse():
        return ColorHSI()

#-----------------------------------------------------------------------

class ColorHCL(ColorModel):
    """
    HCL color model 'luma/chroma/hue' (renamed for consitency)

    hue = [0, 360]
    chroma = [0, 1]
    luma =[0, 1]

    Use Y'_601 = 0.30*R + 0.59*G + 0.11*B

    http://en.wikipedia.org/wiki/HSL_and_HSV#Color-making_attributes
    """
    limits = np.array([[0., 360.],[0., 1.],[0., 1.]])
    _perm = np.array([[0,1,2],[1,0,2],[2,0,1],[2,1,0],[1,2,0],[0,2,1]])
    _luma_vec = np.array([0.30, 0.59, 0.11])
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        h, c, y, mode = cls._args_to_vectors(args)
        h = np.mod(h, 360.)
        c = np.clip(c,0,1, out = c)
        y = np.clip(y,0,1, out = y)
        p = h / 60.
        x = c * (1 - np.abs(np.mod(p, 2.) - 1.))
        z = np.zeros_like(x)
        ip = np.int64(p)
        col = np.vstack((c,x,z)).transpose()        
        rgb = col[np.tile(np.arange(len(x)),(3,1)).transpose(),cls._perm[ip]]
        m = y - np.dot(rgb, cls._luma_vec)
        rgb += m[:,np.newaxis]
        rgb = np.clip(rgb,0,1, out = rgb)
        return cls._array_to_return(rgb, mode)
    @staticmethod
    def _inverse():
        return ColorHCLInverse()
    @classmethod
    def gray(cls, *args):
        __doc__ = ColorModel.gray.__doc__
        return cls.inverse(ColorRGB().gray(*args))

class ColorHCLInverse(ColorModel):
    """
    Convert RGB to HCL.


    Return:
      hue = [0, 360]
      chroma = [0, 1]
      luma =[0, 1]

    http://en.wikipedia.org/wiki/HSL_and_HSV#Color-making_attributes
    """
    range = ColorHCL.limits
    _luma_vec = ColorHCL._luma_vec
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        r, g, b, mode = cls._args_to_vectors(args)
        r = clip(r,1,0)
        g = clip(g,1,0)
        b = clip(b,1,0)        
        M = np.maximum(r,np.maximum(g,b))
        m = np.minimum(r,np.minimum(g,b))
        C = M - m
        h = np.zeros_like(C)        
        i = np.logical_and(M == r, C > 0)
        h[i] = np.mod((g[i]-b[i])/C[i],6)
        i  = np.logical_and(M == g, C > 0)
        h[i] = (b[i]-r[i])/C[i] + 2 
        i = np.logical_and(M == b, C > 0)
        h[i] = (r[i]-g[i])/C[i] + 4
        H = h * 60
        y = np.dot(np.array([r, g, b]).transpose(), cls._luma_vec)
        return cls._vectors_to_return(H,C,y, mode)
    @staticmethod
    def _inverse():
        return ColorHCL()

#-----------------------------------------------------------------------

class ColorHCL2(ColorHCL):
    """
    HCL color model 'luma/chroma/hue' (renamed for consitency)

    Input:
      hue = [0, 360]
      chroma = [0, 1]
      luma =[0, 1]

    Use Y'709 = 0.21*R + 0.72*G + 0.07*B

    http://en.wikipedia.org/wiki/HSL_and_HSV#Color-making_attributes
    """
    limits = np.array([[0., 360.],[0., 1.],[0., 1.]])
    _perm = np.array([[0,1,2],[1,0,2],[2,0,1],[2,1,0],[1,2,0],[0,2,1]])
    _luma_vec = np.array([0.21, 0.72, 0.07])
    @staticmethod
    def _inverse():
        return ColorHCL2Inverse()

class ColorHCL2Inverse(ColorHCLInverse):
    """
    Convert RGB to HCL.

    Return:
      hue = [0, 360]
      chroma = [0, 1]
      luma =[0, 1]

    Use Y'709 = 0.21*R + 0.72*G + 0.07*B

    http://en.wikipedia.org/wiki/HSL_and_HSV#Color-making_attributes
    """
    range = ColorHCL.limits
    _luma_vec = ColorHCL2._luma_vec
    @staticmethod
    def _inverse():
        return ColorHCL2()

#-----------------------------------------------------------------------

class ColorYIQ(ColorModelMatrix):
    """
    YIQ color model.

    y = [0, 1]
    |i| <= 0.596
    |q| <= 0.523

    'gray' value:  I = Q = 0
    """
    limits = np.array([[0., 1.],[-0.596, +0.596],[-0.523, +0.523]])
    _matrixI = np.matrix(
        [[0.299, 0.587, 0.114],
         [0.596,-0.275,-0.321],
         [0.212,-0.523, 0.311]])
    _matrix = _matrixI.getI()
    _gray_index = [1,2]
    _gray_value = [0,0]
    @staticmethod
    def _inverse():
        return ColorYIQInverse()

class ColorYIQInverse(ColorModelMatrix):
    """
    Convert RGB to YIQ.

    Return:
      y = [0, 1]
      |i| <= 0.596
      |q| <= 0.523
    """
    range = ColorYIQ.limits
    _matrix = ColorYIQ._matrixI
    @staticmethod
    def _inverse():
        return ColorYIQ()

#-----------------------------------------------------------------------

class ColorYUV(ColorModelMatrix):
    """
    YUV color model.

    Input:
      y = [0, 1]
      |u| <= 0.436
      |v| <= 0.615

    Rec. 601

    http://en.wikipedia.org/wiki/YUV
    """
    limits = np.array([[0., 1.],[-0.436, +0.436],[-0.615, +0.615]])
    _matrix = np.matrix(
        [[ 1, 0      , 1.13983],
         [ 1,-0.39465,-0.58060],
         [ 1, 2.03211, 0      ]])
    _gray_index = [1,2]
    _gray_value = [0,0]
    @staticmethod
    def _inverse():
        return ColorYUVInverse()

class ColorYUVInverse(ColorModelMatrix):
    """
    Convert RGB to YUV.

    Return:
      y = [0, 1]
      |u| <= 0.436
      |v| <= 0.615

    Rec. 601

    http://en.wikipedia.org/wiki/YUV
    """
    range = ColorYUV.limits
    _matrix = np.matrix(
        [[ 0.299  , 0.587   , 0.114  ],
         [-0.14713,-0.28886 , 0.463  ],
         [ 0.615  ,-0.551499,-0.10001]])
    @staticmethod
    def _inverse():
        return ColorYUV()

#-----------------------------------------------------------------------

class ColorYUV2(ColorModelMatrix):
    """
    YUV color model.

    Input:
      y = [0, 1]
      |u| <= 0.436 (?)
      |v| <= 0.615 (?)

    Rec. 709

    http://en.wikipedia.org/wiki/YUV
    """
    limits = np.array([[0., 1.],[-0.436, +0.436],[-0.615, +0.615]])
    _matrix = np.matrix(
        [[ 1, 0      , 1.28033],
         [ 1,-0.21482,-0.38059],
         [ 1, 2.12798, 0      ]])
    _gray_index = [1,2]
    _gray_value = [0,0]
    @staticmethod
    def _inverse():
        return ColorYUV2Inverse()

class ColorYUV2Inverse(ColorModelMatrix):
    """
    Convert RGB to YUV.

    Return:
      |u| <= 0.436 (?)
      |v| <= 0.615 (?)

    Rec. 709

    http://en.wikipedia.org/wiki/YUV
    """
    range = ColorYUV.limits
    _matrix = np.matrix(
        [[ 1, 0      , 1.28033],
         [ 1,-0.21482,-0.38059],
         [ 1, 2.12798, 0      ]])
    @staticmethod
    def _inverse():
        return ColorYUV2()

#-----------------------------------------------------------------------

class ColorYCbCr(ColorModelMatrix):
    """
    YCrCb color model.

    Input:
      y = floating-point value between 16 and 235
      Cb, Cr: floating-point values between 16 and 240
    """
    limits = np.array([[16., 235.],[16., 240.],[16., 240.]])
    _matrix = np.matrix(
        [[ 1, 0    , 1.402  ],
         [ 1,-0.344,-0.714  ],
         [ 1,+1.772, 0      ]])
    @staticmethod
    def _inverse():
        return ColorYCbCrInverse()
    @classmethod
    def _transform(cls, a):
        return (np.inner(a, cls._matrix) - np.array([0.,128.,128.])[np.newaxis,:]) / 256. 
    @classmethod
    def gray(cls, *args):
        __doc__ = ColorModel.gray.__doc__
        return cls.inverse(ColorRGB().gray(*args))

class ColorYCbCrInverse(ColorModelMatrix):
    """
    Convert RGB to YCbCr.

    Return:
      y = floating-point value between 16 and 235
      Cb, Cr: floating-point values between 16 and 240
    """
    range = ColorYCbCr.limits
    _matrix = np.matrix(
        [[ 0.299  , 0.587   , 0.114  ],
         [-0.169  ,-0.331   , 0.499  ],
         [ 0.499  ,-0.418   ,-0.0813 ]])
    @classmethod
    def _transform(cls, a):
        return np.inner(a * 256 + np.array([0.,128.,128.])[np.newaxis,:], cls._matrix)  
    @staticmethod
    def _inverse():
        return ColorYCrCb()

#-----------------------------------------------------------------------

class ColorYDbDr(ColorModelMatrix):
    """
    YDrDb color model.

    Input:
      y = [0, 1]
      Db, Dr: [-1.333, +1.333]

    http://en.wikipedia.org/wiki/YDbDr
    """
    limits = np.array([[0., 1.],[-1.333,1.333],[-1.333,1.333]])
    _matrixI = np.matrix(
        [[ 0.299  , 0.587   , 0.114  ],
         [-0.450  ,-0.883   ,+1.333  ],
         [-1.333  , 1.116   , 0.217 ]])
    _matrix = _matrixI.getI()
    @staticmethod
    def _inverse():
        return ColorYDbDrInverse()
    @classmethod
    def gray(cls, *args):
        __doc__ = ColorModel.gray.__doc__
        return cls.inverse(ColorRGB().gray(*args))

class ColorYDbDrInverse(ColorModelMatrix):
    """
    Convert RGB to YDbDr.

    Return:
      y = [0, 1]
      Db, Dr: [-1.333, +1.333]

    http://en.wikipedia.org/wiki/YDbDr
    """
    range = ColorYDbDr.limits
    _matrix = ColorYDbDr._matrixI
    @staticmethod
    def _inverse():
        return ColorYDrDb()

#-----------------------------------------------------------------------

class ColorYPbPr(ColorModelMatrix):
    """
    YPbPr color model.

    Input:
      y = [0, 1]
      Pb,Pr = [-0.5, 0.5]
    """
    limits = np.array([[0., 1.],[-0.5, 0.5],[-0.5, 0.5]])
    _R = 0.2126 
    _G = 0.7152 
    _B = 0.0722
    _matrixI = np.matrix(
        [[  _R,  _G,  _B],
         [ -_R, -_G,1-_B],
         [1-_R, -_G, -_B]])
    _matrix = _matrixI.getI()
    _gray_index = [1,2]
    _gray_value = [0,0]
    @staticmethod
    def _inverse():
        return ColorYPbPrInverse()

class ColorYPbPrInverse(ColorModelMatrix):
    """
    Convert RGB to YPbPr.

    Return:
      y = [0, 1]
      Pb,Pr = [-0.5, 0.5]
    """
    range = ColorYPbPr.limits
    _matrix = ColorYPbPr._matrixI
    @staticmethod
    def _inverse():
        return ColorYPbPr()

#-----------------------------------------------------------------------

class ColorXYZ(ColorModelMatrix):
    """
    CIE XYZ color model.

    Input:
       X, Y, Z
    """
    _scale = 1. #/0.17697
    limits = np.array([[0., 1.],[0., 1.],[0., 1.]]) * _scale 
    _matrixI = np.matrix(
        [[0.49   ,0.31   ,0.20   ],
         [0.17697,0.81240,0.01063],
         [0.00   ,0.01   ,0.99   ]]) * _scale
    _matrix = _matrixI.getI()
    @staticmethod
    def _inverse():
        return ColorXYZInverse()
    @classmethod
    def gray(cls, *args):
        __doc__ = ColorModel.gray.__doc__
        return cls.inverse(ColorRGB().gray(*args))

class ColorXYZInverse(ColorModelMatrix):
    """
    Convert RGB to XYZ.

    Return:
      X, Y, Z
    """
    range = ColorXYZ.limits
    _matrix = ColorXYZ._matrixI
    @staticmethod
    def _inverse():
        return ColorXYZ()

#-----------------------------------------------------------------------

class ColorLMS(ColorModelMatrix):
    """
    CIE CAT02 LMS color model.

    Input:
       L, M, S
    """
    _MCAT02 = np.matrix(
        [[ 0.7328, 0.4296,-0.1624],
         [-0.7036, 1.6975, 0.0061],
         [ 0.0030, 0.0136, 0.9834]])
    _matrixI = np.matrix(np.inner(_MCAT02, ColorXYZ._matrixI.transpose()))
    limits = np.inner(_MCAT02,  ColorXYZ.limits.transpose())
    _matrix = _matrixI.getI()
    @staticmethod
    def _inverse():
        return ColorLMSInverse()
    @classmethod
    def gray(cls, *args):
        __doc__ = ColorModel.gray.__doc__
        return cls.inverse(ColorRGB().gray(*args))

class ColorLMSInverse(ColorModelMatrix):
    """
    Convert RGB to LMS.

    CIE CAT02 LMS color model.

    Return:
      L, M, S
    """
    range = ColorLMS.limits
    _matrix = ColorLMS._matrixI
    @staticmethod
    def _inverse():
        return ColorLMS()

#-----------------------------------------------------------------------

class ColorxyY(ColorModel):
    """
    CIE xyY color model.

    Input:
       x, y, Y

       http://en.wikipedia.org/wiki/Chromaticity_coordinate
    """
    limits = np.array([[-1., 1.],[-1., 1.],ColorXYZ.limits[1]]) 
    @staticmethod
    def _inverse():
        return ColorxyYInverse()
    @classmethod
    def gray(cls, *args):
        __doc__ = ColorModel.gray.__doc__
        return cls.inverse(ColorRGB().gray(*args))
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        x,y,Y, mode = cls._args_to_vectors(args)
        Yy = np.ones_like(y)
        ind = y != 0
        Yy[ind] = Y[ind]/y[ind]
        X = Yy * x
        Z = Yy * (1. - x - y)
        rgb = ColorXYZ()(np.vstack((X,Y,Z)).transpose())
        return cls._array_to_return(rgb, mode)

class ColorxyYInverse(ColorModel):
    """
    Convert RGB to xyY.

    Return:
      x, y, Y
    """
    range = ColorxyY.limits
    @staticmethod
    def _inverse():
        return ColorxyY()
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        r,g,b, mode = cls._args_to_vectors(args)
        X,Y,Z = ColorXYZInverse()(r,g,b)
        s = X + Y + Z
        ind = s != 0
        si = 1./s
        x = np.zeros_like(X)
        y = np.zeros_like(Y)
        x[ind] = X * si
        y[ind] = Y * si
        return cls._vectors_to_return(x,y,Y, mode)

#-----------------------------------------------------------------------

class ColorLab(ColorModel):
    """
    CIE L*a*b* color model

    use D65 (6504 K)
    X=95.047, Y=100.00, Z=108.883
    http://en.wikipedia.org/wiki/CIE_Standard_Illuminant_D65
    http://en.wikipedia.org/wiki/Lab_color_space
    """
    _Xn = 95.047
    _Yn = 100.00
    _Zn = 108.883
    limits = np.array([[-1,1],[-1,1],[-1,1.]])*np.inf
    @staticmethod
    def _inverse():
        return ColorLabInverse()
    @classmethod
    def gray(cls, *args):
        __doc__ = ColorModel.gray.__doc__
        return cls.inverse(ColorRGB().gray(*args))
    def _fn(x):
            ind = x > 6./29.
            y = x.copy()
            y[ind] = x[ind]**3
            ind = np.logical_not(ind)
            y[ind] = 3.*(6/29.)**2*(x-4/29.)
            return y
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        L,a,b, mode = cls._args_to_vectors(args)
        Y = cls._Yn * cls._fn((L+16.)/116.)
        X = cls._Xn * cls._fn((L+16.)/116. + a/500.)
        Z = cls._Zn * cls._fn((L+16.)/116. - b/200.)
        rgb = ColorXYZ()(np.vstack((X,Y,Z)).transpose())
        return cls._array_to_return(rgb, mode)
    
class ColorLabInverse(ColorModel):
    """
    CIE L*a*b* color model

    use D65 (6504 K)
    X=95.047, Y=100.00, Z=108.883
    http://en.wikipedia.org/wiki/CIE_Standard_Illuminant_D65
    http://en.wikipedia.org/wiki/Lab_color_space
    """
    range = ColorLab.limits
    _Xn = ColorLab._Xn
    _Yn = ColorLab._Yn
    _Zn = ColorLab._Zn
    @staticmethod
    def _inverse():
        return ColorLab()
    @staticmethod
    def _f(x):
        y = x.copy()
        ind = x > (6./29.)**3
        y[ind] = x[ind]**(1./3.)
        ind = np.logical_not(ind)
        y[ind] = 1./3.*(29./6.)**2 * x + 4./29.
        return y
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        r,g,b, mode = cls._args_to_vectors(args)
        X,Y,Z = ColorXYZInverse()(r,g,b)
        L = 116. *  cls._f(Y / cls._Yn) - 16.
        a = 500. * (cls._f(X / cls._Xn) - cls._f(Y / cls._Yn))
        b = 200. * (cls._f(Y / cls._Yn) - cls._f(Z / cls._Zn))
        return cls._vectors_to_return(L,a,b, mode)
 
#-----------------------------------------------------------------------

class ColorLab2(ColorModel):
    """
    Hunter/Adams Lab color model

    use D65 (6504 K)
    X=95.047, Y=100.00, Z=108.883
    http://en.wikipedia.org/wiki/CIE_Standard_Illuminant_D65
    http://en.wikipedia.org/wiki/Lab_color_space
    """
    _Xn = 95.047
    _Yn = 100.00
    _Zn = 108.883

    _Ka = 175./198.04 * (_Xn + _Yn)
    _Kb =  70./218.11 * (_Yn + _Zn)
    _K  = _Ka / 100.
    _ke = _Ka / _Kb

    limits = np.array([[-1,1],[-1,1],[-1,1.]])*np.inf
    @staticmethod
    def _inverse():
        return ColorLab2Inverse()
    @classmethod
    def gray(cls, *args):
        __doc__ = ColorModel.gray.__doc__
        return cls.inverse(ColorRGB().gray(*args))
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        L,a,b, mode = cls._args_to_vectors(args)
        ind = L != 0
        ca = np.ones_like(L)
        cb = np.ones_like(L)
        Y = (L / 100.)**2 * cls._Yn
        ca[ind] = a[ind] / (cls._K * L[ind])
        cb[ind] = b[ind] / (cls._K * L[ind])        
        X = (ca + 1.) * (Y / cls._Yn) * cls._Xn
        Z = (1. - (cb / cls._ke))  * (Y / cls._Yn) * cls._Zn
        rgb = ColorXYZ()(np.vstack((X,Y,Z)).transpose())
        return cls._array_to_return(rgb, mode)
    
class ColorLab2Inverse(ColorModel):
    """
    Hunter/Adams Lab color model

    use D65 (6504 K)
    X=95.047, Y=100.00, Z=108.883
    http://en.wikipedia.org/wiki/CIE_Standard_Illuminant_D65
    http://en.wikipedia.org/wiki/Lab_color_space
    """
    range = ColorLab.limits
    _Xn = ColorLab2._Xn
    _Yn = ColorLab2._Yn
    _Zn = ColorLab2._Zn

    _Ka = ColorLab2._Ka
    _Kb = ColorLab2._Kb
    _K =  ColorLab2._K
    _ke = ColorLab2._ke

    @staticmethod
    def _inverse():
        return ColorLab2()
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        r,g,b, mode = cls._args_to_vectors(args)
        X,Y,Z = ColorXYZInverse()(r,g,b)
        ind = Y != 0
        ca = np.ones_like(Y)
        cb = np.ones_like(Y)
        L = 100. * np.sqrt(Y / cls._Yn)
        ca[ind] =      (X[ind] / cls._Xn) / (Y[ind] / cls._Yn) - 1.
        cb[ind] = cls._ke * (1. - (Z[ind] / cls._Zn) / (Y[ind] / cls._Yn))
        a = cls._K * L * ca
        b = cls._K * L * cb
        return cls._vectors_to_return(L,a,b, mode)
 
#-----------------------------------------------------------------------
# there seems to be an issue that LMS can return negative values.

class ColorCAM(ColorModel):
    """
    CIECAM02 

    http://en.wikipedia.org/wiki/CIECAM02

    """
    limits = np.array([[-1,1],[-1,1],[-1,1.]])*np.inf
    _LW = 100. # cd/m^2
    _Yb =  20. # luminace of background
    _Yw = 100. # luminace of reference white
    _LA = _LW * _Yb / _Yw # suppsed to be LW/5 for 'gray'

    _F = 1. # factor determining degree of adaptation

    _D = _F * (1. - 1./3.6 * np.exp((-_LA + 42.)/92.)) # The degree of adaptation
    # _D = 0 # no adaptation

    # reference white
    _Lwr = _Mwr = _Swr = _Ywr = 100
    # illuminant white
    _Lw = _Mw = _Sw = _Yw = 100

    _fL = (1. + (_Yw * _Lwr / (_Ywr * _Lw) - 1.)* _D)
    _fM = (1. + (_Yw * _Mwr / (_Ywr * _Mw) - 1.)* _D)
    _fS = (1. + (_Yw * _Swr / (_Ywr * _Sw) - 1.)* _D)

    _MCAT02 = ColorLMS._MCAT02

    _MH = np.matrix(
        [[ 0.38971, 0.68898,-0.07868],
         [-0.22981, 1.18340, 0.04641],
         [ 0.00000, 0.00000, 1.00000]])

    _ML = np.inner(_MCAT02, _MH.getI().transpose())

    _k = 1./(5.* _LA + 1.)
    _FL = 1./5. * _k**4*(5.*_LA) + 1./10. * (1. - _k**4)**2 * (5.*_LA)**(1./3.)

    @staticmethod
    def _inverse():
        return ColorCAMInverse()
    @classmethod
    def gray(cls, *args):
        __doc__ = ColorModel.gray.__doc__
        return cls.inverse(ColorRGB().gray(*args))
    @classmethod
    def _fn(cls, y):
        y1 = y - 0.1
        xp = y1 * 27.13 / (400. - y1)
        x = xp **(1./0.42) * 100. / cls._FL
        return x
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        Lap,Map,Sap, mode = cls._args_to_vectors(args)
        Lp = cls._fn(Lap)
        Mp = cls._fn(Map)
        Sp = cls._fn(Sap)
        Lc, Mc, Sc = np.inner(cls._ML, np.array([Lp, Mp, Sp]).transpose())
        L = Lc / cls._fL 
        M = Mc / cls._fM 
        S = Sc / cls._fS 
        r,g,b = ColorLMS()(L,M,S)
        return cls._vectors_to_return(r,g,b, mode)
    
class ColorCAMInverse(ColorModel):
    """
    CIE CAM02 

    http://en.wikipedia.org/wiki/CIECAM02

    """
    range = ColorCAM.limits

    _LW = 100. # cd/m^2
    _Yb =  20. # luminace of background
    _Yw = 100. # luminace of reference white
    _LA = _LW * _Yb / _Yw # suppsed to be LW/5 for 'gray'

    _F = 1. # factor determining degree of adaptation

    _D = _F * (1. - 1./3.6 * np.exp((-_LA + 42.)/92.)) # The degree of adaptation
    # _D = 0 # no adaptation

    # reference white
    _Lwr = _Mwr = _Swr = _Ywr = 100
    # illuminant white
    _Lw = _Mw = _Sw = _Yw = 100

    _fL = (1. + (_Yw * _Lwr / (_Ywr * _Lw) - 1.)* _D)
    _fM = (1. + (_Yw * _Mwr / (_Ywr * _Mw) - 1.)* _D)
    _fS = (1. + (_Yw * _Swr / (_Ywr * _Sw) - 1.)* _D)

    _MH = np.matrix(
        [[ 0.38971, 0.68898,-0.07868],
         [-0.22981, 1.18340, 0.04641],
         [ 0.00000, 0.00000, 1.00000]])

    _MCAT02 = ColorLMS._MCAT02

    _ML =  np.inner(_MH, _MCAT02.getI().transpose())

    _k = 1./(5.* _LA + 1.)
    _FL = 1./5. * _k**4*(5.*_LA) + 1./10. * (1. - _k**4)**2 * (5.*_LA)**(1./3.)

    @staticmethod
    def _inverse():
        return ColorCAM()
    @classmethod
    def _f(cls, x):
        xp = (cls._FL * x / 100.)**0.42
        y = 400.* xp / (27.13 + xp) + 0.1
        return y
    @classmethod
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        r,g,b, mode = cls._args_to_vectors(args)
        L,M,S = ColorLMSInverse()(r,g,b)        

        Lc = cls._fL * L
        Mc = cls._fM * M
        Sc = cls._fS * S

        Lp, Mp, Sp = np.clip(np.inner(cls._ML, np.array([Lc, Mc, Sc]).transpose()),0,np.inf)

        Lap = cls._f(Lp)
        Map = cls._f(Mp)
        Sap = cls._f(Sp)

        return cls._vectors_to_return(Lap,Map,Sap, mode)
 
#-----------------------------------------------------------------------

class ColorsRGB(ColorModel):
    """
    sRGB color model ICE 61966-2-1

    """
    @staticmethod
    def _s(x):
        mask = x > 0.04045
        x[mask] = ((x[mask] + 0.055)/1.055)**2.4
        mask = np.logical_not(mask)
        x[mask] = x[mask]/12.92
        return np.clip(x, 0, 1, out = x)
    @classmethod    
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        sRGB, mode = cls._args_to_array(args)        
        rgb = np.apply_along_axis(cls._s, -1, sRGB)
        return cls._array_to_return(rgb, mode)
        # sR, sG, sB, mode = cls._args_to_vectors(args)        
        # r = cls._s(sR) 
        # g = cls._s(sG) 
        # b = cls._s(sB) 
        # return cls._vectors_to_return(r,g,b, mode)
    @staticmethod
    def _inverse():
        return ColorsRGBInverse()

class ColorsRGBInverse(ColorModel):
    """
    Convert RGB to sRGB.

    """
    @staticmethod
    def _s(x):
        mask = x > 0.04045/12.92
        x[mask] = x[mask]**(1/2.4) * 1.055 - 0.055
        mask = np.logical_not(mask)
        x[mask] = x[mask] * 12.92
        return np.clip(x, 0, 1, out = x)    
    @classmethod    
    def __call__(cls, *args):
        __doc__ = ColorModel.__call__.__doc__
        rgb, mode = cls._args_to_array(args)        
        sRGB = np.apply_along_axis(cls._s, -1, rgb)
        return cls._array_to_return(sRGB, mode)
    @staticmethod
    def _inverse():
        return ColorsRGB()

#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

# register color models

_color_models = dict()
def register_color_model(name, model):
    assert isinstance(name, str)
    assert issubclass(type(model), ColorModel)
    _color_models[name] = model
def color_models():
    return _color_models
def color_model(model = 'RGB'):
    return _color_models[model]

register_color_model('RGB', ColorRGB())
register_color_model('CMY', ColorCMY())
register_color_model('HSV', ColorHSV())
register_color_model('HSL', ColorHSL())
register_color_model('HSI', ColorHSI())
register_color_model('HCL', ColorHCL()) # Rev 601, seems also go as 'yCH'
register_color_model('HCL2', ColorHCL()) # Rev 709, seems also go as 'yCH'
register_color_model('YIQ', ColorYIQ()) 
register_color_model('YUV', ColorYUV()) # Rev 601 
register_color_model('YUV2', ColorYUV2()) # Rev 709
register_color_model('YCbCr', ColorYCbCr()) 
register_color_model('YDbDr', ColorYDbDr()) 
register_color_model('YPbPr', ColorYPbPr()) 
register_color_model('XYZ', ColorXYZ()) # CIE XYZ 
register_color_model('LMS', ColorLMS()) # CIE CAM 02 LMS
register_color_model('xyY', ColorxyY()) # CIE xyY
register_color_model('Lab', ColorLab()) # CIE L*a*b*, 6504 K 
register_color_model('Lab2', ColorLab2()) # Hunter Lab, 6504 K 
register_color_model('CAM', ColorCAM()) # CIE CAM 02 
register_color_model('sRGB', ColorsRGB()) # IEC 61966-2-1 


#######################################################################
#######################################################################
# Define Color[Function] as a replacement for Colormap

def colormap(name, **kwargs):
    if isinstance(name, ColorMap):
        return name
    c = get_cfunc(name)
    if c is None:
        try:
            c = ColorMap.from_Colormap(name, **kwargs)
        except:
            pass
    return c

class Color(colors.Colormap):
    """
    Base class to provide color map functionallity but on 'color
    function' basis.

    Users may overwrite the __init__ routing to set up coloring functions.
    This should usually call the base method provided here.

    The main coloring is done in the function _function.  The values,
    normalized to 0..1, will be passed as a 1D array for simplicity.
    If the class attribute _alpha is False (default) it is assumed
    _function will return a numpy array of RGB values (:,3) and an
    array of RGBA values (:.4) otherwise, also normalized to the range
    0...1.

    Much of the remaining functionallity should be very similar to
    color maps.
    """
    bytes = False # default for bytes
    _alpha = False # tell whether function computes alpha
    def __init__(self, *args, **kwargs):
        self.bytes = kwargs.get('bytes', False)
        self.name  = kwargs.get('name', self.__class__.__name__)
        self.alpha = kwargs.get('alpha', 1.)

        self._rgba_bad = np.array([0.0, 0.0, 0.0, 0.0])  # If bad, don't paint anything.
        self._rgba_under = None
        self._rgba_over = None        
    def __call__(self, data, *args, **kwargs):
        """
        Process data and return RGBA value.
        """
        kw = dict(kwargs)
        alpha     = kw.setdefault('alpha', None)
        normalize = kw.setdefault('normalize', None)
        bytes     = kw.setdefault('bytes', self.bytes)
        data, shape = self._input_to_data(data, normalize)
        if alpha is not None:
            alpha = np.clip(alpha, 0., 1.)
        mask_bad   = np.logical_not(np.isfinite(data))
        mask_under = data < 0
        mask_over  = data > 1
        mask = np.logical_not(
            np.logical_or(
                np.logical_or(
                    mask_bad, 
                    mask_under),
                mask_over))
        out = self._get_out(data, mask, *args, **kw)

        # SIMPLE TREATMENT FOR INVALID/LOW/HIGH DATA
        if self._rgba_under is None:
            self._rgba_under = self._default_color(0., *args, **kw)
        if self._rgba_over is None:
            self._rgba_over = self._default_color(1., *args, **kw)
        out[mask_under,:] = self._rgba_under
        out[mask_over ,:] = self._rgba_over
        if alpha is not None:
            out[:,-1] = alpha
        out[mask_bad  ,:] = self._rgba_bad

        return self._return(out, shape, bytes)
    
    def _default_color(self, x, alpha, *arg, **kw):
        return self._get_out(np.array([x]), alpha, *arg, **kw)[0]

    def _get_out(self, data, mask = None, *args, **kw):
        out = np.ndarray((data.size,4))
        if mask is None:
            mask = np.tile(True, data.size)
        if self._alpha:
            out[mask,:] = self._function(data[mask], *args, **kw)
        else:
            out[mask,:3] = self._function(data[mask], *args, **kw)
            out[:   , 3] = self.alpha
        return out

    def _function(data, *args, **kwargs):
        """
        prototype conversion

        # if self._alpha:
        #     out = np.tile(data, 4).reshape(-1,4)
        # else:
        #     out = np.tile(data, 3).reshape(-1,3)
        """
        raise NotImplementedError()

    def _update_alpha(self, alpha):
        """
        compute output array
        """
        
        if not self._alpha:
            if alpha is None:
                alpha = 1.
            else:
                out[:,3] = alpha
        return alpha
    @staticmethod
    def _input_to_data(data, normalize):
        """
        Normalize and get shape
        """
        # May need to allow other formats as well.
        if not isinstance(data, np.ndarray):
            data = np.asarray(data)
        if normalize in (None, True):
            M = data.max()
            m = data.min()
            if normalize is None: 
                normalize = m < 0. or M > 1.
        if normalize:
            d = M - m
            if d == 0:
                d = 1.
            data = (data - m) / d
        shape = data.shape
        data  = data.reshape(-1)
        return data, shape

    def _return(self, out, shape, bytes):
        """
        output conversion
        """
        out = out.reshape(list(shape) + [-1])
        if bytes is None:
            bytes = self.bytes
        if bytes:
            out = np.array(np.minimum(out*256,255), dtype = np.ubyte)
        return out
        
    def Colormap(self, N = 256, name = None):
        """
        Return matplotlib.colors.Colormap object with N levels.
        """
        x = np.linspace(0,1,N)
        if name is None:
            name = self.name
        cm = colors.ListedColormap(
            self.__call__(x), 
            name = name, 
            N = N)
        cm.set_bad(self._rgba_bad)
        cm.set_under(self._rgba_under)
        cm.set_over(self._rgba_over)
        return cm

    def set_bad(self, color='k', alpha=None):
        '''
        Set color to be used for masked values.
        '''
        if alpha is None:
            alpha = self.alpha
        self._rgba_bad = colorConverter.to_rgba(color, alpha)


    def set_under(self, color='k', alpha=None):
        '''
        Set color to be used for low out-of-range values.
        Requires norm.clip = False
        '''
        if alpha is None:
            alpha = self.alpha
        self._rgba_under = colorConverter.to_rgba(color, alpha)

    def set_over(self, color='k', alpha=None):
        '''
        Set color to be used for high out-of-range values.
        Requires norm.clip = False
        '''
        if alpha is None:
            alpha = self.alpha
        self._rgba_over = colorConverter.to_rgba(color, alpha)

    def _set_extremes(self):
        pass

    def _init(self):
        raise NotImplementedError("Color Function")

    def is_gray(self):
        """
        Return whether color is gray.
        """
        # Subclasses may overwrite this.
        return False

    _N = 1024
    def get_N(self):
        return self._N
    N = property(get_N)    

_colors = dict()
def register_color(name, color):
    assert isinstance(name, str)
    assert isinstance(color, Color)
    assert not _colors.has_key(name)
    _colors[name] = color

def get_cfunc(name):
    """
    return color_function object of given name
    """
    return _colors.get(name, None)

class ColorMap(Color):
    _alpha = True
    def __init__(self, 
                 map = None,
                 layout = None,
                 model = None,
                 color = None,
                 models = None,
                 normalize = None,
                 gamma = 1.,
                 gamma_func = None,
                 **kwargs):
        """
        Set up Color Map.

        This is based on Color[functions].  The power is that the
        methed alloes arbitraty smooth/fine interpolation.

        model: color model to use
        models: list of models for numeric values
        color: use this color if not given in layout
        alpha: alpha value
        layout: [X][C|CCC][A][G|GG|GGG|GGGG][M][N]
             X: coordinate, non-zero values normalized to [0,1]
             XXXX: gamma for each color and alpha
             C: grayscale
             CCC: three color values
             A: alpha
             G: gamma, same for all
             GG: gamma for color and alpha
             GGG: gamma for three colors but not alpha
             GGGG: gamma for each color and alpha
             M: model
             N: normalize (see below)
        map: use <0 for invalid data?
        bytes: - set default
        normalize: normalize valuse to valid range
             None| -1: auto-determine
             True| +1: yes
             False| 0: no
           Normalization is based on [0,1] range is given, translate
           to valid range for parameters.
        
        NOTES:
        
        X coordinates < 0:
          [bad [, lower, upper]]

        The interval generally is scaled lineraly so that X[-1]
        becomes 1.
          
        In each interval each component is interpolated from the
        begiing to end value according to the a function normalized to
        0...1 for the interval.  The scaling itself is detemined by
        the 'gamma' parameter at the end of the interval, so the first
        values is ignored, and so are the gamma for negiative indices
        (see above).
     
        gamma can be a scalar, then it is interpreted as a power for
        interpolation in an interval.  
  
          
        """
        alpha = kwargs.get('alpha', None)
        super(ColorMap, self).__init__(**kwargs)
        self._gamma = kwargs.get('gamma', 1.)

        assert layout is not None
        layout = layout.upper()

        ncoord = layout.count('X')
        assert ncoord in (0,1,4), "can 0,1, or 4 coordinates"
        ipos = layout.find('X')
        if ncoord == 0 :    
            if map.ndim == 1:
                n = map.size
            else:
                n = map.shape[0]
            coord = np.arange(n).reshape((1, ncoord))
            ncoord = 1
        else:
            n = map.shape[0]
            coord = np.ndarray((n, ncoord))
            for i in xrange(ncoord):
                coord[:,i] = map[:,ipos]
                ipos = layout.find('X', ipos + 1)
        if coord.dtype is not np.float64:
            coord = np.array(coord, dtype = np.float64)
        for j in xrange(ncoord):
            ii = coord[:,j] >= 0
            i, = np.where(ii)
            coord[ii,j] -= coord[i[0],j]
            coord[ii,j] /= coord[ii,j].max()

        assert layout.count('A') < 2, "can have only one alpha value"
        ipos = layout.find('A')
        if ipos >= 0:
            alpha = map[:,ipos]
        else:   
            if alpha == None:
                alpha = 1.
            alpha = np.tile(alpha, n)
        
        assert layout.count('N') < 2, "can have only one normalization value"
        ipos = layout.find('N')
        if ipos >= 0:
            normal = map[:,ipos]
        else:   
            if normalize == -1:
                normalize = None
            normal = np.tile(normalize, n)
        norm = np.empty_like(normal, dtype = np.object)
        for i,x in enumerate(normal):
            if x == 1:
                x == True
            elif x == 0:
                x = False
            else:
                x = None
            norm[i] = x
        normal = norm

        assert layout.count('M') < 2, "can have only one model value"
        ipos = layout.find('M')
        if ipos >= 0:
            model = map[:,ipos]
        else:   
            if model == None:
                model = 0
            model = np.tile(model, n)

        # models is converted to array of color objects
        if models == None:
            models = ['RGB', 'HSV', 'HSL', 'HSI']
        models = np.array(models).reshape(-1)
        m = np.empty_like(model, dtype = np.object)
        for i,x in enumerate(model):
            if not isinstance(x, str):
                x = models[x]
            m[i] = _color_models[x.upper()]
        model = m

        nc = layout.count('C')
        assert nc in (1,3), "Color has to be C or CCC"
        if nc == 0:
            if color == None:
                color = 0.
            if len(color) == 1:
                color = np.array([mx.gray(color) for mx in model])
            elif len(color) == 3:
                color = np.tile(color, (3,1))
            else:
                raise AttributeError("Wrong format in 'color' keyword.")
        if nc == 1:
            ipos = layout.find('C')
            c = map[:,ipos]
            color = np.array([mx.gray(cx) for (mx, cx) in zip(model, c)])
        else:
            color = np.ndarray((n,3))
            ipos = -1
            for i in xrange(3):
                ipos = layout.find('C', ipos + 1)
                color[:,i] = map[:,ipos]
        # normalize
        # 1) auto-detect
        d = dict()
        for i in xrange(n):
            if normal[i] is None:
                m = model[i]
                c = color[i]
                try:
                    limits = d[m]
                    limits[:,0] = np.minimum(limit[:,0],c)
                    limits[:,1] = np.maximum(limit[:,1],c)
                except:
                    limits = np.tile(c,(2,1)).transpose()
                d[m] = limits
        for m,l in d.items():    
            d[m] = not m.is_normal(l)
        # 2) do normalization
        for i in xrange(n):
            m = model[i]
            if normal[i] is None:
                normal[i] = d[m]
            if normal[i]:
                color[i,:] = m.normalize(color[i,:])
                
        # combine color and alpha
        color = np.hstack((color, alpha.reshape(-1,1)))

        # ADD/TREAT 'invalid' colors [bad [, lower, upper]]
        ii = coord[:, 0] < 0
        im,= np.where(ii)
        assert im.size in (0,1,3), "Only [bad [, lower, upper]] allowed for 'invalid' colors"
        if im.size > 0:
            i = im[0]
            self._rgba_bad = np.hstack((model[i](color[i,0:3]),color[i,3]))
            if im.size > 1:
                i = im[1]
                self._rgba_lower = np.hstack((model[i](color[i,0:3]),color[i,3]))
                i = im[2]
                self._rgba_upper = np.hstack((model[i](color[i,0:3]),color[i,3]))
            jj = np.logical_not(ii)
            map   = map  [:,jj]
            color = color[:,jj]
            model = model[:,jj]
            coord = coord[:,jj]
            
        # convert to N x 4 array for gamma
        ng = layout.count('G')
        assert nc in (1,3), "Gamma has to be G, GG, GGG, or GGGG"
        if ng == 0:
            gamma = np.tile(1., (n,4))    
        if ng == 1:
            ipos = layout.find('G')
            g = map[:,ipos]
            gamma = np.tile(g,(4,1)).transpose()
        if ng == 2:
            ipos = layout.find('G')
            g = map[:,ipos]
            gamma = np.tile(g,(4,1)).transpose()
            ipos = layout.find('G', ipos+1)
            g = map[:,ipos]
            gamma[:,3] = g
        if ng == 3:
            gamma = np.ndarray((n,4), dtype = map.dtype)
            ipos = -1
            for i in xrange(3):
                ipos = layout.find('G', ipos + 1)
                gamma[:,i] = map[:,ipos]
            gamma[:,3] = np.tile(1., n)    
        if ng == 4:
            gamma = np.ndarray((n,4), dtype = map.dtype)
            ipos = -1
            for i in xrange(4):
                ipos = layout.find('G', ipos + 1)
                gamma[:,i] = map[:,ipos]        

        # translate to functions
        if gamma_func == None:
            gamma_func = lambda x, gamma: np.power(x, gamma)
        assert isinstance(gamma_func, types.FunctionType), (
            "gamma_func needs to be a function")
        if gamma.dtype == np.object:
            g = gamma
        else:
            g = np.empty_like(gamma, dtype = object)
        identiy = lambda x: x
        for i,f in enumerate(gamma.flat):
            if not isinstance(f, types.FunctionType):
                if f is None:
                    g.flat[i] = identity 
                else:
                    g.flat[i] = partial(gamma_func, gamma = f)    
        gamma = g

        # save setup
        self.n = n
        self.gamma = gamma
        self.color = color
        self.model = model
        self.coord = coord
        self.ncoord = ncoord

    def _function(self, data, *args, **kwargs):
        out = np.ndarray((data.size, 4))
        coord = self.coord ** (1 / self._gamma) # gamma from LinearSegmentedColormap
        assert self.ncoord in (1,4), "require consisient set of gamma"
        if self.ncoord == 1:
            # use np.piecwise instead?
            color0 = self.color[0,:]
            coord0 = coord[0,0]
            for i in xrange(1, self.n):
                if self.model[i-1] != self.model[i]:
                    color0[0:3] = self.model[i].inverse()(self.model[i-1](color0[0:3]))
                color1 = self.color[i,:]
                coord1 = coord[i,0]
                if coord0 < coord1: # allow discontinuous maps
                    ind = np.logical_and(data >= coord[i-1], data <= coord[i]) 
                    if np.count_nonzero(ind):
                        dcolor = color1 - color0
                        dcoord = coord1 - coord0
                        colcoord = (data[ind] - coord0) / dcoord
                        for j in xrange(4):
                            out[ind,j] = color0[j] + self.gamma[i,j](colcoord)*dcolor[j]
                        if self.model[i] != _color_models['RGB']:
                            out[ind,0:3] = self.model[i](out[ind,0:3])
                color0 = color1
                coord0 = coord1
        else:
            assert np.all(self.model[0] == self.model[:]),'All color models need to be equal if using independent coordinates'
            for j in xrange(4):
                coord0 = coord[0, j]
                color0 = self.color[0,j]
                for i in xrange(1, self.n):
                    color1 = self.color[i,j]
                    coord1 = coord[i, j]
                    if coord0 < coord1: # allow discontinuous maps
                        ind = np.logical_and(data >= coord0, data <= coord1) 
                        if np.count_nonzero(ind):
                            dcolor = color1 - color0
                            dcoord = coord1 - coord0                            
                            colcoord = (data[ind] - coord0) / dcoord
                            out[ind, j] = color0 + self.gamma[i,j](colcoord)*dcolor
                    color0 = color1
                    coord0 = coord1
            if self.model[0] != _color_models['RGB']:
                 # transform only valid data
                 ind = np.logical_and(data >= 0, data <= 1)
                 out[ind,0:3] = self.model[i](out[ind,0:3])        
        return out

    @staticmethod
    def from_Colormap_spec(colors, **kwargs):
        if not ('red' in colors):            
            assert isinstance(colors, Iterable)
            if (isinstance(colors[0], Iterable) and 
                len(colors[0]) == 2 and 
                not is_string_like(colors[0])):
                # List of value, color pairs
                vals, colors = zip(*colors)
            else:
                vals = np.linspace(0., 1., len(colors))            
            map = np.ndarray([[val] + list(colorConverter.to_rgba(color)) for val, color in zip(vals, colors)])
            return ColorMap(map, layout = 'XCCCA', **kwargs)
        if callable(colors['red']):
            map = np.array([np.zeros(9), np.ones(9)], dtype = object)
            map[1,5] = lambda x: np.clip(colors['red'](x),0,1)
            map[1,6] = lambda x: np.clip(colors['green'](x),0,1)
            map[1,7] = lambda x: np.clip(colors['blue'](x),0,1)
            if 'alpha' in colors:
                map[1,8] = lambda x: np.clip(colors['alpha'],0,1)
            else:
                map[0,4] = 1.
            return ColorMap(map, layout = 'XCCCAGGGG', **kwargs)
        xmap = []
        for c in ('red', 'green', 'blue', 'alpha'):
            color = colors.get(c, None)
            if color == None: 
                if c == 'alpha':
                    color = ((0,0,1.), (1,1,1.))
                else:
                    color = ((0,0,0.), (1,1,0.))
            color = np.array(color)
            shape = color.shape
            assert len(shape) == 2
            assert shape[1] == 3
            # copied from matplotlib.color.py
            x  = color[:, 0]
            y0 = color[:, 1]
            y1 = color[:, 2]
            if x[0] != 0. or x[-1] != 1.:
                raise ValueError("data mapping points must start with x=0. and end with x=1")
            if np.sometrue(np.sort(x) - x):
                raise ValueError("data mapping points must have x in increasing order")
            # end copy
            xc = [[x[0], y1[0]]]
            for i in xrange(1,shape[0]-1):
                xc += [[x[i], y0[i]]]
                if y0[i] != y1[i]:
                    xc += [[x[i], y1[i]]]
            i = shape[0]-1        
            xc += [[x[i], y0[i]]]
            xmap += [np.array(xc)]
        nn = np.array([len(xc) for xc in xmap])
        n = np.max(nn)
        map = np.ones((n,8))
        for i,xc in enumerate(xmap):
            map[0:nn[i],i::4] = xc              
        if np.all(map[:,0:4] == map[:,0][:,np.newaxis]):
            map = map[:,3:]
            layout = 'XCCCA'
        else:
            layout = 'XXXXCCCA'       
        return ColorMap(map, layout = layout, **kwargs)


    @staticmethod
    def from_Colormap(map, name = None, gamma = None, **kwargs):
        if isinstance(map, ColorMap):
            return map
        if isinstance(map, str):
            name = map
            map = get_cmap(name)
        if isinstance(map, LinearSegmentedColormap):
            segmentdata = map._segmentdata
            if gamma is not None:
                gamma = map._gamma
            rgba_bad = map._rgba_bad
            rgba_under = map._rgba_under
            rgba_over = map._rgba_over
            if name is not None:
                name = map.name
            f = ColorMap.from_Colormap_spec(
                segmentdata, 
                name = name, 
                gamma = gamma,
                **kwargs)
            if rgba_under is not None:
                f.set_under(rgba_under)
            if rgba_over is not None:
                f.set_over(rgba_over)
        else:
            if gamma is None:
                gamma = 1.0
            f = ColorMap.from_Colormap_spec(
                map, 
                name = name,
                gamma = gamma,
                **kwargs)
        return f     
            
#######################################################################
# Some specific color maps & examples

class ColorMapGal(ColorMap):
    maps = {
        0: np.array(
            [[0,0,0,1,0], 
             [5,0,0,0,2], 
             [7,1,0,0,0.5]]),
        1: np.array(
            [[0,1,1,1,0], 
             [2,0,1,0,2], 
             [3,0,0.75,0.75,1], 
             [4,0,0,1,1], 
             [5,0,0,0,1], 
             [6,1,0,0,1], 
             [7,1,1,0,0.75]]),
        2: np.array(
            [[0,1,1,1,0], 
             [2,0,1,0,2], 
             [3,0,0.75,0.75,1], 
             [4,0,0,1,1], 
             [6,1,0,0,1], 
             [7,1,1,0,0.75]]),
        3: np.array(
            [[0,1,1,1,0],
             [2,0,1,0,2], 
             [3,0,1,1,1], 
             [4,0,0,1,1], 
             [5,1,0,1,1], 
             [6,1,0,0,1], 
             [6.25,1,.75,0,2]]),
        4: np.array(
            [[0,1,1,1,0],
             [1,.75,.75,.75,2],
             [2,0,1,0,2], 
             [3,0,1,1,1], 
             [4,0,0,1,1], 
             [5,1,0,1,1], 
             [6,1,0,0,1], 
             [6.25,1,.75,0,2]])
        }
    _len =  len(maps)
    def __init__(self, mode = 1):
        try: 
            map = self.maps[mode]
        except:
            raise AttributeError('Invalid mode')
        super(ColorMapGal, self).__init__(
            map = map, 
            layout = 'XCCCG')

for i in xrange(ColorMapGal._len):
    register_color('GalMap{:d}'.format(i), ColorMapGal(i))


class ColorMapGray(ColorMap):
    maps = {
        0:  np.array(
            [[0,0,0], 
             [1,1,1]]), 
        1:  np.array(
            [[0,0,0],
             [1,1,lambda x: 0.5*(1-np.cos(x*np.pi))]]), 
        }
    _len =  len(maps)
    def __init__(self, mode = 0):
        try: 
            map = self.maps[mode]
        except:
            raise AttributeError('Invalid mode.')
        super(ColorMapGray, self).__init__(
            map = map, 
            layout = 'XCG')
    @staticmethod
    def is_gray():
        return True

for i in xrange(ColorMapGray._len):
    register_color('GrayMap{:d}'.format(i), ColorMapGray(i))


class ColorRGBWaves(Color):
    """
    red-green-blue+waves
    """
    _alpha = False
    def __init__(self, nwaves = 200, **kwargs):
        super(ColorRGBWaves, self).__init__(**kwargs)
        self.waves = nwaves*np.pi
        self._N = np.max((np.round(12*nwaves), 1024))
    def _function(self,x, *args, **kwargs):
        return _color_models['HSV'](np.array([
                    300 * x,
                    x**0.5,
                    1 - 0.25 * (np.sin(x*self.waves)**2)
                    ]).transpose())

register_color('RGBWaves200', ColorRGBWaves(200))

class ColorRKB(Color):
    """
    red-black-blue
    """
    _alpha = False
    def _function(self,x, *args, **kwargs):
        def theta(x):
            y = np.zeros_like(x)
            y[x<0] = -1
            y[x>0] = +1
            return y
        return _color_models['HSV'](np.array([
                    30+180*x+30*theta(x-0.5),
                    np.ones_like(x),
                    np.minimum(5*np.abs(x - 0.5),1)
                    ]).transpose())

register_color('RKB', ColorRKB())

class ColorBWR(ColorMap):
    """
    blue white red with adjustable white at paramter value
    """
    def __init__(self, 
                 white = 0.5, 
                 gamma = 2.0, 
                 **kwargs):
        assert 0 <= white <= 1
        assert gamma > 0
        map = np.array(
            [[0    ,0,0,1,0.0], 
             [white,1,1,1,gamma], 
             [1    ,1,0,0,1./gamma]])
        super(ColorBWR, self).__init__(
            map = map, 
            layout = 'XCCCG',
            **kwargs)

register_color('BWR', ColorBWR())


class ColorBWGRY(ColorMap):
    """
    red white blue with adjustable white at paramter value
    """
    def __init__(self, 
                 p = 0.5, 
                 **kwargs):
        assert 0 <= p <= 1
        p13 = (1-p)/3
        map = np.array(
            [[0      ,0,0,1,0.00], 
             [p      ,1,1,1,2.00], 
             [1-2*p13,0,1,0,1.00], 
             [1-1*p13,1,0,0,0.85], 
             [1      ,1,1,0,1]])
        super(ColorBWGRY, self).__init__(
            map = map, 
            layout = 'XCCCG',
            **kwargs)

register_color('BWGRY', ColorBWGRY())

class ColorKRGB(Color):
    """
    red-green-blue+waves
    """
    _alpha = False
    def __init__(self, **kwargs):
        super(ColorKRGB, self).__init__(**kwargs)
    def _function(self,x, *args, **kwargs):
        return _color_models['HSV'](np.array([
                    x*270,
                    np.ones_like(x),
                    np.minimum(10*x,1)
                    ]).transpose())

register_color('KRGB', ColorKRGB())

class ColorBWC(ColorMap):
    """
    grey-white-color
    """
    def __init__(self, 
                 p = 0.5,
                 mode = 0,
                 **kwargs):
        assert 0 <= p <= 1
        p2 = (1-p)/3 + p
        if mode == 0:
            map = np.array(
                [[0 ,   0,0,0,0.], 
                 [p , 120,0,1,1.], 
                 [p2, 120,1,1,2.], 
                 [1 ,-120,1,1,1.]])
        elif mode == 1:
            map = np.array(
                [[0 ,  0,0,0,0.], 
                 [p ,120,0,1,1.], 
                 [p2,120,1,1,2.], 
                 [1 ,420,1,1,1.]])
        elif mode == 2:
            f = lambda x: np.sin(0.5*x*np.pi)
            map = np.array(
                [[0 ,  0,0,0,0.], 
                 [p ,240,0,1,1.], 
                 [p2,240,1,1,f], 
                 [1 ,-30,1,1,1.]])
        else:
            map = np.array(
                [[0 ,  0,0,0,0.], 
                 [p ,240,0,1,1.], 
                 [p2,240,1,1,1.], 
                 [1 ,-30,1,1,1.]])
        super(ColorBWC, self).__init__(
            map = map, 
            layout = 'XCCCG',
            model = 'HSV',
            normalize = False,
            **kwargs)

register_color('BWC', ColorBWC())

class ColorMapFunction(ColorMap):
    """
    generate color function form color map by linear interpolation
    """
    def __init__(self, name):
        pass

#######################################################################

from matplotlib.colors import rgb2hex

def isocolors(n, start=0, stop=360):
    h = np.linspace(start, stop, n, endpoint = False)
    return np.array([rgb2hex(color_model('HSV')(hi,1,1)) for hi in h ]) 
         
def isogray(n, start=0, stop=1, endpoint=False):
    h = np.linspace(start, stop, n, endpoint = endpoint)
    return np.array([rgb2hex(g) for g in color_model('RGB').gray(h)]) 
         
def isoshadecolor(n, start=0, stop=1, hue = 0, endpoint = False):
    h = np.linspace(start, stop, n, endpoint = endpoint)
    return np.array([rgb2hex(color_model('HSV')(hue,1-hi, 1)) for hi in h[::-1] ]) 
         

#######################################################################
#######################################################################
#######################################################################
    
def test():
    N = 1000
    x = np.exp(np.linspace(-2.0, 3.0, N))
    y = np.exp(np.linspace(-2.0, 2.0, N))
    x = (np.linspace(-2.0, 3.0, N))
    y = (np.linspace(-2.0, 2.0, N))

    X, Y = np.meshgrid(x, y)    
    X1 = 0.5*(X[:-1,:-1] + X[1:,1:])
    Y1 = 0.5*(Y[:-1,:-1] + Y[1:,1:])

    from matplotlib.mlab import bivariate_normal
    Z1 = bivariate_normal(X1, Y1, 0.1, 0.2, 1.27, 1.11) + 100.*bivariate_normal(X1, Y1, 1.0, 1.0, 0.23, 0.72)

    ZR = bivariate_normal(X1, Y1, 0.1, 0.2, 1.27, 1.11) + 100.*bivariate_normal(X1, Y1, 1.0, 1.0, 0.23, 0.72)
    ZG = bivariate_normal(X1, Y1, 0.1, 0.2, 2.27, 0.11) + 100.*bivariate_normal(X1, Y1, 1.0, 1.0, 0.43, 0.52)
    ZB = bivariate_normal(X1, Y1, 0.1, 0.2, 0.27, 2.11) + 100.*bivariate_normal(X1, Y1, 1.0, 1.0, 0.53, 0.92)
    ZA = bivariate_normal(X1, Y1, 0.1, 0.2, 3.27,-1.11) + 100.*bivariate_normal(X1, Y1, 1.0, 1.0, 0.23, 0.82)

    Z = np.ndarray(ZR.shape + (4,))
    Z[...,0] = ZR /ZR.max()
    Z[...,1] = ZG /ZG.max()
    Z[...,2] = ZB /ZB.max()
    Z[...,3] = np.exp(-ZA /ZA.max())

    Z = (Z*255).astype(np.uint8)

    fig = plt.figure()    

    Z1[Z1>0.9*np.max(Z1)] = +np.inf

    ax = fig.add_subplot(1,1,1)
    # col = plt.get_cmap('terrain_r')
    # col = get_cfunc('RGBWaves200')
    col = plt.get_cmap('gnuplot2')
    col = colormap('cubehelix')
    col = colormap('RGBWaves200')
    col = ColorBWC(mode=0)
    i = ax.pcolorfast(x, y, Z1, cmap = col)
    # i = ax.pcolorfast(x, y, Z)

    # from matplotlib.image import PcolorImage
    # i = PcolorImage(ax, x, y, Z)
    # ax.images.append(i)
    # xl, xr, yb, yt = x[0], x[-1], y[0], y[-1]
    # ax.update_datalim(np.array([[xl, yb], [xr, yt]]))
    # ax.autoscale_view(tight=True)
    plt.colorbar(i)
    plt.show()
    return i


from matplotlib.image import PcolorImage
def pcolorimage(ax, x, y, Z):
    """
    Make a PcolorImage based on Z = (x, z, 4) [byte] array 

    This is to fix an omission ('bug') in the current (as of this
    writing) version of MatPlotLib.  I may become superfluous in the
    future.
    """
    img = PcolorImage(ax, x, y, Z)
    ax.images.append(img)
    xl, xr, yb, yt = x[0], x[-1], y[0], y[-1]
    ax.update_datalim(np.array([[xl, yb], [xr, yt]]))
    ax.autoscale_view(tight=True)
