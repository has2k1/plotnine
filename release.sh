#!/usr/bin/env sh

# Since a release is just a make command away, and the versions
# are determined by the tag, we check to make sure that HEAD
# is appropriately tagged for release.

color=$(tput setaf 1)   # message color
tcolor=$(tput setaf 2)  # tag color
reset=$(tput sgr0)      # reset color codes
describe=$(git describe --always)

# The tag is FULLY recognised as a nice version
good_version=$(echo $describe | grep '^v[0-9]\+\.[0-9]\+\.[0-9]\+$')

# Partial recognition of a nice version, and maybe more stuff
# This may give us the previous version.
known_version=$(echo $describe | grep -o '^v[0-9]\+\.[0-9]\+\.[0-9]\+')

if [[ $good_version ]];  then
   python setup.py sdist bdist_wheel
   twine upload dist/*

elif [[ $known_version ]]; then
  last_release=$(echo $known_version | tr -d v)
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
  - major release:$tcolor git tag -a v$tmajor -m 'Version: $tmajor'\
$reset"

else
   echo -e "\
$color
You must create a version tag before releasing,
For example: $tcolor

\tgit tag -a v0.1.0 -m 'Version: v0.1.0'\
$reset"

fi
