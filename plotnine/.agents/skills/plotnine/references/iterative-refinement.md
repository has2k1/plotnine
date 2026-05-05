# Iterative Refinement

When revising existing plot code, make the smallest change that achieves the
user's request. This file defines the protocol for editing, presenting changes,
and deciding when to start fresh.

## Iterative Edit Protocol

Follow these five rules when revising plot code:

1. **Minimal changes** — modify only the lines that address the user's request.
   Do not rewrite surrounding code, rename variables, or rearrange layers
   unless the user asks for that.

2. **"What changed / Why" summary** — after each revision, state what changed
   and why in 1-2 sentences.

3. **Before/after for non-trivial changes** — when the change involves more
   than adding or removing a single line, show the relevant before and after
   code.

4. **Preserve user's style** — if the user uses `theme_bw()`, keep it. If they
   use `import plotnine as p9`, keep that import style. Don't impose different
   conventions.

5. **Never rewrite unless structurally necessary** — changing the chart type
   (e.g., scatter to bar) requires a fresh plot. Adding a layer, adjusting
   scales, or changing theme elements does not.

## Diff Protocol

Present changes with this template:

```
**What changed:** Added `geom_smooth(method="lm")` layer.
**Why:** User asked for a linear trend line.
```

For multi-line changes, show the code delta:

````
**What changed:** Replaced default scale with colorblind-safe palette and added
shape encoding.

```python
# Before
    + geom_point()

# After
    + geom_point(aes(shape="species"))
    + scale_color_brewer(type="qual", palette="Set2")
```

**Why:** User asked for colorblind-friendly colors.
````

## Common Revision Patterns

| User request | Minimal code change |
|-------------|-------------------|
| "Add a trend line" | `+ geom_smooth(method="lm")` |
| "Add a loess smoother" | `+ geom_smooth()` |
| "Make it cleaner" | Swap to `theme_minimal()` or `theme_bw()` |
| "Change colors" | Add or replace `scale_color_*` / `scale_fill_*` |
| "Facet by X" | `+ facet_wrap("X")` |
| "Rotate x labels" | `+ theme(axis_text_x=element_text(rotation=45, ha="right"))` |
| "Remove legend" | `+ theme(legend_position="none")` |
| "Add labels" | Update `labs(title=..., x=..., y=...)` |
| "Make points bigger" | Change `size=` parameter in `geom_point()` |
| "Add transparency" | Add `alpha=` parameter to the relevant geom |
| "Flip axes" | `+ coord_flip()` |
| "Log scale" | `+ scale_y_log10()` or `+ scale_x_log10()` |

## Full Before/After Example

**User:** "Add a linear trend line to this scatter plot."

### Before

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.6)
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Fuel Efficiency")
)
```

### After

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.6)
    + geom_smooth(method="lm")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Fuel Efficiency")
)
```

**What changed:** Added `geom_smooth(method="lm")` after `geom_point`.
**Why:** User requested a linear trend line.

## When to Start Fresh vs Patch

| Scenario | Action |
|----------|--------|
| Adding a layer (trend line, rug, text) | Patch: add the `+` line |
| Changing aesthetics (new color mapping) | Patch: edit `aes()` and add scale |
| Swapping theme | Patch: replace `theme_*()` line |
| Changing chart type (scatter → bar) | Start fresh: different aes + geom |
| Different dataset | Start fresh: different aes + data |
| Restructuring data flow (new groupby, melt) | Start fresh or major rewrite |

## Common Pitfalls

- **Rewriting the entire plot for a layer addition**: If the user says "add a
  trend line," don't rewrite the ggplot call, aes mappings, labs, and theme.
  Just add `+ geom_smooth(method="lm")`.

- **Changing data prep for a visual request**: "Change the color palette" does
  not require modifying the DataFrame. Only change data prep if the user's
  request involves the data itself.

- **Inconsistent `labs()` after `aes()` change**: When adding a new aesthetic
  (e.g., `color="species"`), also update `labs(color="Species")` to provide a
  readable legend title.

- **Forgetting to explain the change**: Always provide the "What changed / Why"
  summary. The user should understand the revision without diffing the code
  themselves.

## See Also

- [geoms.md](geoms.md) — available layers to add
- [aesthetics-and-scales.md](aesthetics-and-scales.md) — scale adjustments
- [themes-and-styling.md](themes-and-styling.md) — theme customizations
