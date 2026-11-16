# python version comes from .python-version through run_test.sh
ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

# requirements first, so this slow layer is reused until requirements.pip changes
COPY requirements.pip .
RUN python -m venv .venv \
    && .venv/bin/python -m pip install --no-cache-dir -r requirements.pip

COPY . .

# the settings of run_test.sh come in as environment, an argument replaces TEST_PATH
ENTRYPOINT ["./run_engine.sh"]
