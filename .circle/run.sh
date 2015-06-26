#!/bin/sh

set -e

VERSION=$1

export PATH=~/.pyenv/shims:$PATH
eval "$(pyenv init -)"

pyenv shell $VERSION
git clean -dfX
python setup.py install
python setup.py test
