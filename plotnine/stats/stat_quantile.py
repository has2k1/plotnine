from warnings import warn

import pandas as pd

from ..doctools import document
from ..exceptions import PlotnineWarning
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
    quantiles : tuple, default=(0.25, 0.5, 0.75)
        Quantiles of y to compute
    formula : str, default="y ~ x"
        Formula relating y variables to x variables
    method_args : dict, default=None
        Extra arguments passed on to the model fitting method,
        [](`~statsmodels.regression.quantile_regression.QuantReg.fit`).

    See Also
    --------
    plotnine.geom_quantile : The default `geom` for this `stat`.
    statsmodels.regression.quantile_regression.QuantReg
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "quantile"  # quantile
    "group"     # group identifier
    ```

    Calculated aesthetics are accessed using the `after_stat` function.
    e.g. `after_stat('quantile')`{.py}.
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "quantile",
        "position": "identity",
        "na_rm": False,
        "quantiles": (0.25, 0.5, 0.75),
        "formula": "y ~ x",
        "method_args": {},
    }
    CREATES = {"quantile", "group"}

    def setup_params(self, data):
        params = self.params
        if params["formula"] is None:
            params["formula"] = "y ~ x"
            warn("Formula not specified, using '{}'", PlotnineWarning)
        try:
            iter(params["quantiles"])
        except TypeError:
            params["quantiles"] = (params["quantiles"],)

    def compute_group(self, data, scales):
        res = [
            quant_pred(q, data, self.params) for q in self.params["quantiles"]
        ]
        return pd.concat(res, axis=0, ignore_index=True)


def quant_pred(q, data, params):
    """
    Quantile precitions
    """
    import statsmodels.formula.api as smf

    mod = smf.quantreg(params["formula"], data)
    reg_res = mod.fit(q=q, **params["method_args"])
    out = pd.DataFrame(
        {
            "x": [data["x"].min(), data["x"].max()],
            "quantile": q,
            "group": f"{data['group'].iloc[0]}-{q}",
        }
    )
    out["y"] = reg_res.predict(out)
    return out
