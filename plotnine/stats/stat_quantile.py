from __future__ import absolute_import, division, print_function

from warnings import warn

import pandas as pd
import statsmodels.formula.api as smf

from ..doctools import document
from .stat import stat


# method_args are any of the keyword args (other than q) for
# statsmodels.regression.quantile_regression.QuantReg.fit
@document
class stat_quantile(stat):
    """
    Compute quantile regression lines

    {usage}

    Parameters
    ----------
    {common_parameters}
    quatiles : tuple, optional (default: (0.25, 0.5, 0.75))
        Quantiles of y to compute
    formula : str, optional (default: 'y ~ x')
        Formula relating y variables to x variables
    method_args : dict, optional
        Extra arguments passed on to the model fitting method,
        :meth:`statsmodels.regression.quantile_regression.QuantReg.fit`.

    {aesthetics}

    .. rubric:: Options for computed aesthetics

    ::

         '..quantile..'  # quantile
         '..group..'     # group identifier

    See Also
    --------
    * :class:`statsmodels.regression.quantile_regression.QuantReg`
    * :class:`~plotnine.geoms.geom_quantile`
    """
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'quantile', 'position': 'identity',
                      'na_rm': False, 'quantiles': (0.25, 0.5, 0.75),
                      'formula': 'y ~ x', 'method_args': {}}
    CREATES = {'quantile', 'group'}

    def setup_params(self, data):
        params = self.params.copy()
        if params['formula'] is None:
            params['formula'] = 'y ~ x'
            warn("Formula not specified, using '{}'")
        try:
            iter(params['quantiles'])
        except TypeError:
            params['quantiles'] = (params['quantiles'],)

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        res = [quant_pred(q, data, **params)
               for q in params['quantiles']]
        return pd.concat(res, axis=0, ignore_index=True)


def quant_pred(q, data, **params):
    mod = smf.quantreg(params['formula'], data)
    reg_res = mod.fit(q=q, **params['method_args'])
    out = pd.DataFrame({
        'x': [data['x'].min(), data['x'].max()],
        'quantile': q,
        'group': '{}-{}'.format(data['group'].iloc[0], q)})
    out['y'] = reg_res.predict(out)
    return out
