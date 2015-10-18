from __future__ import absolute_import, division, print_function

import pandas as pd
import statsmodels.formula.api as smf

from ..utils.exceptions import gg_warn
from .stat import stat


# method_args are any of the keyword args (other than q) for
# statsmodels.regression.quantile_regression.QuantReg.fit
class stat_quantile(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'quantile', 'position': 'identity',
                      'quantiles': (0.25, 0.5, 0.75), 'formula': None,
                      'method_args': {}}

    def setup_params(self, data):
        params = self.params.copy()
        if params['formula'] is None:
            params['formula'] = 'y ~ x'
            msg = "Formula not specified, using '{}'"
            gg_warn(msg.format(params['formula']))
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
