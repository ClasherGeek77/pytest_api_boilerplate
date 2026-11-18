#!/bin/bash
# run the tests without remembering any pytest syntax
#   ./run_test.sh                                       run what TEST_PATH says below
#   ./run_test.sh tests/api/test_users.py               an argument replaces TEST_PATH
# the machinery lives in run_engine.sh, this file is only the three settings to edit
cd "$(dirname "$0")"

# base test path, edit this line to change what runs by default, variants:
#   TEST_PATH="tests/"                                                          everything
#   TEST_PATH="tests/api/"                                                      all api tests
#   TEST_PATH="tests/api/test_users.py"                                         one file
#   TEST_PATH="tests/api/test_users.py::test_getting_unknown_user_is_not_found" one test
#   TEST_PATH="tests/ -k login"                                                 tests whose name contains "login"
#   TEST_PATH="tests/ -x"                                                       stop at the first failure
TEST_PATH="tests/"

# report file name, written to reports/, edit this line to change it, variants:
#   REPORT_NAME=""                  default: report_<run timestamp>_<test path>.html, filled in at run time
#                                   e.g. report_2024-01-30_16-15-42_tests-api-test_users.py.html
#   REPORT_NAME="smoke.html"        a fixed name (overwritten by the next run)
REPORT_NAME=""

# where the tests run, edit this line to change it, variants:
#   RUN_MODE="local"                on this machine with .venv, needs ./first_setup.sh once
#   RUN_MODE="docker"               inside docker with Dockerfile and docker-compose.yml, needs Docker running, no setup
RUN_MODE="local"

export TEST_PATH REPORT_NAME

if [ "$RUN_MODE" = "docker" ]; then
    if ! command -v docker > /dev/null; then
        echo "docker not found, install Docker first, or set RUN_MODE=\"local\""
        exit 1
    fi
    export PYTHON_VERSION=$(cat .python-version)
    export TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
    mkdir -p reports
    echo "Building the image, quick when nothing changed"
    docker compose build --quiet
    exec docker compose run --rm tests "$@"
fi

exec ./run_engine.sh "$@"
