#!/usr/bin/env sh

# This script makes it easy to recompile install and tryout
# a theme in case of any changes. It assumes the
# sphinx-bootstrap-theme-customizer package is in the same directory
# as the package, i.e one up the git toplevel.

color5=$(tput setaf 5)
reset=$(tput sgr0)      # reset color codes

toplevel=$(git rev-parse --show-toplevel)
bootstrap=$(basename $(ls -d theme/static/bootstrap-*/))

# Compile theme
cd $toplevel/../sphinx-bootstrap-theme-customizer/
./build "$@"

# Copy theme for sphinx to use
rm -rf $toplevel/doc/theme
cp -rf theme $toplevel/doc

# Do a hotswap (it may be enough for us to see the results compared to
# regenerating the html)

cd $toplevel
mkdir -p doc/_build/html/_static/$bootstrap/css
cp $toplevel/doc/{theme/static,_build/html/_static}/$bootstrap/css/bootstrap.min.css

echo "${color5}success${reset}"
