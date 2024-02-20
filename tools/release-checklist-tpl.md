# Release Issue Checklist

Copy the template below the line, substitute (`s/<VERSION>/1.2.3/`) the correct
version and create an [issue](https://github.com/has2k1/plotnine/issues/new).

The first line is the title of the issue

------------------------------------------------------------------------------
Release: plotnine-<VERSION>

- [ ] Upgrade key dependencies if necessary

  - [ ] [mizani](https://github.com/has2k1/mizani)
  - [ ] [matplotlib](https://github.com/matplotlib/matplotlib)
  - [ ] [pandas](https://github.com/pandas-dev/pandas)
  - [ ] [numpy](https://github.com/numpy/numpy)
  - [ ] [scipy](https://github.com/scipy/scipy)
  - [ ] [statsmodels](https://github.com/statsmodels/statsmodels)

- [ ] Upgrade code quality checkers

  - [ ] pre-commit

    ```
    pre-commit autoupdate
    ```

  - [ ] ruff

    ```
    pip install --upgrade ruff
    ```

  - [ ] pyright

    ```sh
    pip install --upgrade pyright
    PYRIGHT_VERSION=$(pyright --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    python -c "
    import pathlib, re
    f = pathlib.Path('pyproject.toml')
    f.write_text(re.sub(r'pyright==[0-9]+\.[0-9]+\.[0-9]+', 'pyright==$PYRIGHT_VERSION', f.read_text()))
    "
    ```

- [ ] Run tests and coverage locally

  ```sh
  git switch main
  git pull origin/main
  make typecheck
  make test
  make coverage
  ```
  - [ ] The tests pass
  - [ ] The coverage is acceptable


- [ ] The latest [online documentation](https://has2k1.github.io/plotnine) builds, be sure to browse


- [ ] Create a release branch

  ```sh
  git switch -c release-v<VERSION>
  ```

- [ ] Tag a pre-release version. These are automatically deployed on `testpypi`

  ```sh
  git tag -as v<VERSION>a1 -m "Version <VERSION>a1"  # e.g. <VERSION>a1, <VERSION>b1, <VERSION>rc1
  git push -u origin release-v<VERSION>
  ```
  - [ ] GHA [release job](https://github.com/has2k1/plotnine/actions/workflows/release.yml) passes
  - [ ] Plotnine test release is on [TestPyPi](https://test.pypi.org/project/plotnine/#history)


- [ ] Update changelog

  ```sh
  nvim doc/changelog.qmd
  git commit -am "Update changelog for release"
  git push
  ```
  - [ ] Update / confirm the version to be released
  - [ ] Add a release date
  - [ ] The [GHA tests](https://github.com/has2k1/plotnine/actions/workflows/testing.yml) pass


- [ ] Tag final version and release

  ```sh
  git tag -as v<VERSION> -m "Version <VERSION>"
  git push
  ```

  - [ ] The [GHA Release](https://github.com/has2k1/plotnine/actions/workflows/release.yml) job passes
  - [ ] [PyPi](https://pypi.org/project/plotnine) shows the new release


- [ ] Update `main` branch

  ```sh
  git switch main
  git merge --ff-only release-v<VERSION>
  git push
  ```


- [ ] Create conda release

  - [ ] Copy _SHA256 hash_. Click view hashes, for the [Source Distribution](https://pypi.org/project/plotnine/<VERSION>/#files) (`.tar.gz`).

  - [ ] Update [plotnine-feedsock](https://github.com/conda-forge/plotnine-feedstock)

    ```sh
    cd ../plotnine-feestock
    git switch main
    git pull upstream main
    git switch -c v<VERSION>
    nvim recipe/meta.yml
    git commit -am  "Version <VERSION>"
    git push -u origin v<VERSION>
    ```
  - [ ] Create a [PR](https://github.com/conda-forge/plotnine-feedstock/pulls)
  - [ ] Complete PR (follow the steps and merge)


- [ ] Add [zenodo badge](https://doi.org/10.5281/zenodo.1325308) to the changelog.
