#!/bin/bash
set -e
cd "$(dirname "$0")"

PYTHON_VERSION=$(cat .python-version)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f1,2)
PYTHON=python$PYTHON_MINOR

# plain python3 is fine too, as long as it is the same minor line
if ! command -v $PYTHON > /dev/null; then
    if command -v python3 > /dev/null &&
        [ "$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')" = "$PYTHON_MINOR" ]; then
        PYTHON=python3
    else
        echo "$PYTHON not found, install Python $PYTHON_VERSION first"
        exit 1
    fi
fi

FOUND_VERSION=$($PYTHON --version | cut -d' ' -f2)
if [ "$FOUND_VERSION" != "$PYTHON_VERSION" ]; then
    echo "Pinned Python is $PYTHON_VERSION but found $FOUND_VERSION, same $PYTHON_MINOR line so continuing"
fi

if [ -d .venv ]; then
    VENV_VERSION=$(.venv/bin/python --version | cut -d' ' -f2)
    VENV_MINOR=$(echo $VENV_VERSION | cut -d. -f1,2)
    if [ "$VENV_MINOR" != "$PYTHON_MINOR" ]; then
        echo ".venv uses Python $VENV_MINOR, rebuilding it with Python $PYTHON_MINOR"
        rm -rf .venv
    fi
fi

if [ ! -d .venv ]; then
    echo "Creating .venv"
    $PYTHON -m venv .venv
fi

echo "Upgrading pip and installing requirements"
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -r requirements.pip

echo "Setup done, next run ./run_test.sh"
