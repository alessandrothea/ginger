#!/bin/bash
# This script is meant to be called by the "script" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

HERE=$(python -c "import os.path; print os.path.dirname( os.path.realpath('${BASH_SOURCE:-$0}') )")

set -e

gcc -dumpversion
g++ -dumpversion
ldd --version
python --version
python -c "import numpy; print('numpy %s' % numpy.__version__)"

# Check if ROOT and PyROOT work
root -b -l -q
python -c "import sys; sys.argv.append('-b'); import ROOT; ROOT.TBrowser()"

# Check that rootpy can be imported
time python -c 'import ginger'
