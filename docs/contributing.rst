.. currentmodule:: ggplot
.. _contributing:

************
Contributing
************

The `ggplot` setup is pretty simple. We favor using files over having many
features packed into 1 file (i.e. all the geoms in 1 file). The reason for
this is in part because we want to make it as easy as possible to contribute
to the project.

There are a few things you should know before you get started. We'll take you
through an example of implementing a new geom. Hopefully this will get you
going in the right direction.


Getting Started
~~~~~~~~~~~~~~~

To start, let's reimplement a geom that we all know and love `geom_point`. It's pretty
straightforward - it's going to take some x and y coordinates and make a
scatterplot. You can look at the code here:

.. ipython:: python

    import matplotlib.pyplot as plt
    from ggplot.geoms import geom

    class geom_point2(geom):
        VALID_AES = ['x', 'y', 'size', 'color', 'alpha', 'shape', 'marker', 'label', 'cmap']
        def plot_layer(self, layer):
            layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
            layer.update(self.manual_aes)
            if "size" in layer:
              layer["s"] = layer["size"]
              del layer["size"]
            if "cmap" in layer:
              layer["c"] = layer["color"]
              del layer["color"]
            plt.scatter(**layer)

Imports
-------

The first thing you probably noticed is the imports. First, we imported `pyplot` as `plt`
since this is the regular convention. `ggplot` uses `pyplot` for (nearly) all plots (as
opposed to axes). This makes things simple and keeps the geoms focused only on doing 1
thing.

The second thing we import is the `geom` object. We'll go into more detail on this in a
second.

.. ipython:: python

    import matplotlib.pyplot as plt
    from ggplot.geoms import geom
    # or "from .geoms import geom" if you add a new geom in ggplot itself
    

Inheriting from `geom`
----------------------

As mentioned previously, all of our `geom_*` and `stat_*` (for the time being) inherit
from `geom`. Each of our geoms inherits from the `geom` object. This is going to give
it the delightful `+` properties that make it possible to magically add layers together.

In addition, it keeps things easy so that when it comes time to render the plot, all of
our plot operations are done using the same type of object.

.. ipython:: python

    from ggplot.geoms import geom


Defining the `aes`
------------------

A core concept of `ggplot` is the aesthetics, or attributes and properties, of your plot.
There are many types of `aes` and not all will be available for each type of plot. Here
is a working list of valid `aes`:

- x: x-axis value
- y: y-axis value
- color (colour): color of a layer
- shape: shape of a point
- size: size of a point or line
- alpha: transparency level of a point
- xintercept
- ymin: min value for a vertical line or a range of points
- ymax: max value for a vertical line or a range of points
- xmin: min value for a horizonal line
- xmax: max value for a horizonal line
- slope: slope of an abline
- intercept: intercept of an abline

For each geom, you must define the `VALID_AES`. This tells `ggplot` which aesthetics to
ignore for a particular geom -- which makes it super easy to combine plots that have
different aesthetics.

Handling Layers
---------------

This is the only method you need to implement when you're creating a new geom. It's
actually quite a simple method. `plot_layer` accepts a `layer` object which is just
a dictionary of data that looks like this:

.. ipython:: python

    example_layer = {
      "x": [1, 2, 3, 4],
      "y": [10, 100, 1000, 10000],
      "color": "red"
    }

There are a few things you should know about layers:

- You can expect that incoming discrete variables (i.e. shape or color), will
  come in with only 1 value.
- You can expect that incoming continuous variables (i.e. x, y) will come in
  as a lists of equal length.

Unfortunately if you're reading this then you're interested in contributing to
`ggplot` which means you'll need to write some `matplotlib` code. Ironically even though
I developed `ggplot` to stop writing `matplotlib`, I now find myself writing more
`matplotlib` in order to support `ggplot`. In any event, the `matplotlib` plot methods
do not have consistent names for their arguments. As a result, there are time when you'll
have to edit names of the variables in your layer in order to accomodate `matplotlib`.
You can see here that we're changing the name of the `size` variable to `s` and the 
`color` variable to `c`.

.. ipython:: python

    if "size" in layer:
      layer["s"] = layer["size"]
      del layer["size"]

    if "cmap" in layer:
      layer["c"] = layer["color"]
      del layer["color"]

Constructing the Plot
---------------------

Making the plot is oftentimes the easiest part of building a geom. The key is the know
which arguments are important for the particular plot you're making. In this case, in order
to make a `geom_point` we need a few basic things:

- x coordinates
- y coordinates
- [optional] color / cmap -- cmap is used for color gradients
- [optional] marker / shape
- [optional] label -- what appears in the legend
- [optional] alpha -- level of transparency
- [optional] size -- size of the point

We need to map each of these arguments to a named argument for the `plt.scatter` function.
Once we've done that, we're going to pass in these arguments using `*args`. Note that for some
plotting methods (such as `plt.plot`), you can't specify certain arguments using `*args` (for
example x and y).

That's It
---------

That's really all you have to do to add a geom! It's actually fairly simple. The core `ggplot`
functions will take care of the layering, faceting, etc. neccessary for advanced plotting.

Adding Unittests
~~~~~~~~~~~~~~~~

* For a new geom/... add a new file in `ggplot/tests`. `test_basics.py`
  shows how to test for both same images output and for backend
  functionality like error catching and adding the right things to
  the ggplot object)
* Add new test files to `ggplot/tests/__init__.py` -> `default_test_modules`
* Run the test with `python tests.py -v -d` (you need `nose` installed)
* Check the images from your tests in the `result_images` -> is everything
  as expected? You can get a side-by-side view in the browser via
  `python visual_tests.py` (will generate a html page in `result_images`
  from the images generated in the test run and open the page in the
  default browser)
* If the images are what you expected: copy the new images
  from the `result_images` dir into the corresponding dir under
  `ggplot/tests/baseline_images`
* Rerun the test to see if everything is ok -> all tests should pass


Pull Requests
~~~~~~~~~~~~~

Some guidelines on contributing to ggplot:

* Please submit a Pull Requests.
* Pull Requests can be submitted as soon as there is code worth discussing.
  Pull Requests track the branch, so you can continue to work after the PR is submitted.
  Review and discussion can begin well before the work is complete,
  and the more discussion the better.
  The worst case is that the PR is closed.
* Pull Requests should generally be made against master
* Pull Requests should be tested, if feasible:
    - bugfixes should include regression tests
    - new behavior should at least get minimal exercise
    - see tests in `ggplot/tests/` subdir and the information above.


Some git
~~~~~~~~

This assumes that you cloned from the original ggplot repository (`origin`) and added your
own fork (`mine`) like this:

.. ipython::

    git clone https://github.com/yhat/ggplot.git # becomes "origin"
    git remote add mine git@github.com:YourName/ggplot.git


* Use a feature branch: `git checkout origin/master ; git checkout -b <feature_name>`
* Commit edits belonging together in one go: `git add <files>; git commit`
* If you need to add or change something to your last commit: `git commit --amend`
* Push to your own clone: `git push mine` (during the first time it will tell you to
  use some more arguments to setup the push for this branch)
* Add commits to your PR: just push them : `git commit; git push mine`
* Rebase against master get the latest changes in master and to see if your changes
  still apply cleanly : `git rebase origin/master`. If there are some conflicting
  changes you will be prompted to cleanup the merge conflict.
* Do not use `git merge origin/master` or your PR will be cluttered with merge 
  messages. (Note: this is only valid for your PRs, not if you push your own code
  to your own repo for others to work against!)
* Force push after a rebase: `git push -f mine`.
* Make changes to old commits (reorder, edits, squash multiple commits into 
  one): `git rebase -i origin/master`:
  
  - reorder the commits be moving lines up and down
  - prefix the commit you want to edit with 'e' and the ones you want to squash
    into the former one with 's'
  - for the edits: use `git commit --amend` or `git commit` and after all your
    edits are done: `git rebase --continue`
  - for the squash: just edit the commit message

* View the commit history: `git log`. To only view the first line of the commit
  message: `git log --oneline`
* view the diff of already `git add`ed files: `git diff --cached`
* Unadd files: `git reset HEAD -- <filename>`. You can add an 'unadd' alias for this
  via `git config --global alias.unadd "reset HEAD --"` -> `git unadd <file>`
