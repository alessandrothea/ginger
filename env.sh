HERE=$(python -c "import os.path; print os.path.dirname( os.path.realpath('${BASH_SOURCE:-$0}') )")

export PYTHONPATH="$HERE:$PYTHONPATH"

echo $PYHONPATH
