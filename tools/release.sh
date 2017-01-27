#!/usr/bin/env sh

# Since a release is just a make command away, and the versions
# are determined by the tag, we check to make sure that HEAD
# is appropriately tagged for release.

color=$(tput setaf 1)   # message color
tcolor=$(tput setaf 2)  # tag color
reset=$(tput sgr0)      # reset color codes
describe=$(git describe --always)

# Regexes to identify the release and pre-release parts of a
# valid (PEP440) python package version
release_re='[0-9]\+\.[0-9]\+\.[0-9]\+'
pre_re='\(\(a\|b\|rc\|alpha\|beta\)[0-9]*\)\?'

# The tag is FULLY recognised as a nice version
VERSION=$(echo $describe | grep "^v${release_re}${pre_re}$")

# Partial recognition of a nice version, and maybe more stuff
# This may give us the previous version.
PREVIOUS_VERSION=$(echo $describe | grep "^v${release_re}${pre_re}")

if [[ $VERSION ]];  then
   python setup.py sdist bdist_wheel
   twine upload dist/*

elif [[ $PREVIOUS_VERSION ]]; then
  last_release=$(echo $PREVIOUS_VERSION | tr -d v)
  major_minor=$(echo $last_release | grep -o '^[0-9]\+\.[0-9]\+')
  major=$(echo $last_release | grep -o '^[0-9]\+')
  minor=$(echo $major_minor | grep -o '[0-9]\+$')
  patch=$(echo $last_release | grep -o '[0-9]\+$')
  tpatch=$major.$minor.$((patch+1))
  tminor=$major.$((minor+1)).0
  tmajor=$((major+1)).0.0
  echo -e "\
$color
You cannot make a release if there are commits made after a tag,
or if the tag does not indicate a release.
git describe gives: $tcolor $describe $color
Create a version tag, here are some suggestions:
  - patch release:$tcolor git tag -a v$tpatch -m 'Version: $tpatch' $color
  - minor release:$tcolor git tag -a v$tminor -m 'Version: $tminor' $color
  - major release:$tcolor git tag -a v$tmajor -m 'Version: $tmajor' $color
  - rc candidate :$tcolor git tag -a v${tmajor}rc -m 'Version: $rcmajor' $color
  - alpha release:$tcolor git tag -a v${tmajor}alpha1 -m 'Version: $rcmajor' $color
  - beta release :$tcolor git tag -a v${tmajor}beta1 -m 'Version: $rcmajor'\
$reset"

else
   echo -e "\
$color
You must create a version tag before releasing,
For example: $tcolor

\tgit tag -a v0.1.0 -m 'Version: v0.1.0'\
$reset"

fi

