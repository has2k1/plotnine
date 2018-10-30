from .position import position
from ..exceptions import PlotnineError


class position_adjust_text(position):
    """
    use an iterative algorithm to adjust text labels
    (geom_text and geom_label) positions after plotting

    Useful to nudge labels away from the points
    being labels.

    Uses https://github.com/Phlya/adjustText
    Look there for adjust_text_params 


    Parameters
    ----------
    adjust_text_params : dictionary of parammeters passed to adjust_text(text, **adjust_text_params)
    
    """
    REQUIRED_AES = {'x', 'y'}
    ALLOWED_GEOMS = {'geom_text', 'geom_label'}

    def __init__(self, adjust_text_params=None):
        self.params = adjust_text_params or {'arrowprops':{'arrowstyle':'->', 'color':'red'}}

    def postprocess_panel(self, ax):
        from adjustText import adjust_text
        texts = [t for t in ax.texts]
        adjust_text(texts, ax=ax, **self.params)

    @classmethod
    def compute_layer(cls, data, params, layout):
        return data
