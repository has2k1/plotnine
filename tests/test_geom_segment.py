import pandas as pd

from plotnine import ggplot, aes, geom_segment, arrow, theme


n = 4

# stepped horizontal line segments
df = pd.DataFrame({
        'x': range(1, n+1),
        'xend': range(2, n+2),
        'y': range(n, 0, -1),
        'yend': range(n, 0, -1),
        'z': range(1, n+1)
    })
_theme = theme(subplots_adjust={'right': 0.85})


def test_aesthetics():
    p = (ggplot(df, aes('x', 'y', xend='xend', yend='yend')) +
         geom_segment(size=2) +
         # Positive slope segments
         geom_segment(aes(yend='yend+1', color='factor(z)'), size=2) +
         geom_segment(aes(yend='yend+2', linetype='factor(z)'), size=2) +
         geom_segment(aes(yend='yend+3', size='z'),
                      show_legend=False) +
         geom_segment(aes(yend='yend+4', alpha='z'), size=2,
                      show_legend=False))

    assert p + _theme == 'aesthetics'


def test_arrow():
    p = (ggplot(df, aes('x', 'y', xend='xend', yend='yend')) +
         geom_segment(aes('x+2', xend='xend+2'),
                      arrow=arrow(), size=2) +
         geom_segment(aes('x+4', xend='xend+4'),
                      arrow=arrow(ends='first'), size=2) +
         geom_segment(aes('x+6', xend='xend+6'),
                      arrow=arrow(ends='both'), size=2)
         )

    assert p == 'arrow'
