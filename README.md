# pytest_api_boilerplate

## what it is

a starter project for REST api tests with Python, pytest and `requests`. it ships with 10 working tests (users: list, get, create, update, delete; auth: login and register) against a local copy of the reqres.in demo api, so you can run something real in minutes and then copy the structure for your own service.

- tests are plain pytest functions in `tests/api/`
- one `HttpClient` logs every request and reply, one client class per service area, one endpoints class for the paths
- every check goes through one `assertion` helper that logs each step
- the target is the reqres.in clone, http://localhost:40000/api: no internet, no rate limits, no daily quota

source: https://github.com/ClasherGeek77/pytest_api_boilerplate (the `legacy` branch holds the full history of its predecessors, pytest_api_automation_framework and api_automation_petstore_swagger).

## when to use it

use it when you want to learn or start an api suite with a clean layout (fixtures, client layer, constants, html reports, optional docker).

not for:

- browser tests: use https://github.com/ClasherGeek77/pytest_web_boilerplate
- the same api tests in Katalon Studio: use https://github.com/ClasherGeek77/katalon_api_boilerplate
- ready-made request collections to click through: https://github.com/ClasherGeek77/postman_collection or https://github.com/ClasherGeek77/bruno_collection
- load tests: use https://github.com/ClasherGeek77/locust_boilerplate

## what you need

| thing | version | where |
|---|---|---|
| Python | 3.8 (the line in `.python-version`, 3.8.2; any 3.8.x works, `first_setup.sh` refuses other lines) | https://www.python.org/downloads/ |
| the reqres.in clone | any commit, Python 3 standard library only | https://github.com/ClasherGeek77/reqresin_clone |
| git, bash | any | Mac and Linux; on Windows use WSL |
| Docker | optional, only for `RUN_MODE="docker"` | https://docs.docker.com/get-docker/ |

python packages (pytest 7.4.4, pytest-html 4.1.1, requests 2.31.0, urllib3 1.26.20, black, bandit, pylint) are pinned in `requirements.pip` and installed by `first_setup.sh`. urllib3 is held on 1.x because 2.x warns on LibreSSL builds of Python, the tests talk plain http anyway.

## quick start

1. get the target and start it. the suite looks for it next to this repo, so clone both into the same folder:

```bash
git clone https://github.com/ClasherGeek77/reqresin_clone.git
git clone https://github.com/ClasherGeek77/pytest_api_boilerplate.git
cd reqresin_clone
python3 server.py
```

you should see `reqres clone on http://localhost:40000/api  (Ctrl-C to stop)`. leave it running. check it from another terminal:

```bash
curl http://localhost:40000/api/users/2
```

you should see JSON with `"first_name": "Janet"`. (`python3 server.py --port 8000` changes the port; then set `BASE_URL` too.)

this step is optional: if nothing answers on `BASE_URL`, the test session starts `server.py` itself from `../reqresin_clone` and stops it after the run.

2. in a second terminal, set this repo up once:

```bash
cd pytest_api_boilerplate
./first_setup.sh                    # builds .venv from requirements.pip
```

you should see `Setup done, next run ./run_test.sh`.

3. run it:

```bash
./run_test.sh
```

every request and reply is logged and the run ends with `10 passed`. the HTML report is written to `reports/report_<timestamp>_tests.html`.

check what exists without running anything:

```bash
.venv/bin/python -m pytest --collect-only -q
```

you should see `10 tests collected` (auth 4, users 6).

one test, with the real output of a run:

```bash
./run_test.sh tests/api/test_users.py::test_getting_existing_user_returns_that_user
```

you should see `sending GET http://localhost:40000/api/users/2`, a `got 200 back with {'data': {'id': 2, 'email': 'janet.weaver@reqres.in', ...` line, three `checking ...` lines, and `1 passed`.

## run one test, or a few

`run_test.sh` takes any pytest argument; an argument replaces the default `TEST_PATH="tests/"` at the top of the script. the variants:

```bash
./run_test.sh tests/api/                                                          # all api tests
./run_test.sh tests/api/test_users.py                                             # one file
./run_test.sh tests/api/test_users.py::test_getting_unknown_user_is_not_found     # one test
./run_test.sh "tests/api/test_auth.py::test_auth_without_password_is_refused[login]"   # one row of a table test
./run_test.sh tests/ -k login                                                     # names containing "login"
./run_test.sh tests/ -x                                                           # stop at the first failure
```

to change the default for every run, edit `TEST_PATH` at the top of `run_test.sh` (same text, e.g. `TEST_PATH="tests/ -k login"`). `REPORT_NAME` there sets a fixed report name such as `smoke.html`; empty means `report_<timestamp>_<test path>.html`. `RUN_MODE` there is `"local"` (default, uses `.venv`) or `"docker"`.

`./checks.sh` runs bandit (security), black (format) and pylint (lint).

## settings

plain `KEY=value` lines in `test.env`, loaded by `run_test.sh` and printed at the start of every run; the tests read them through `lib/constants.py`.

| key | default | meaning |
|---|---|---|
| `BASE_URL` | `http://localhost:40000` | where the reqres clone answers. this is how the suite finds the target. paths in the code start with `/api` |
| `API_TIMEOUT` | `10` | seconds per request |
| `RESET_SERVICES` | `0` | `1` calls `ApiClient.reset_all` before the first and after the last test; keep `0` for reqres (no reset endpoint, `reset_all` raises on purpose) |
| `REQRESIN_CLONE_DIR` | `../reqresin_clone` | where the clone lives, only used when nothing answers on `BASE_URL`. uncomment the line in `test.env` to change it |

## how to read the code

```
conftest.py            fixtures: reqres_clone, setup_session, api, testdata, assertion, logger; class ApiClient bundles the clients
lib/constants.py       environment_data (from test.env) and constant_data (ids, emails, page size, expected fields)
lib/api/endpoints.py   the paths, one class per service (UsersEndpoint, AuthEndpoint)
lib/api/clients.py     one class per service, every method is one or two lines that call get/post/put/delete
lib/api/base.py        HttpClient (logs every request and reply) and ApiResponse (.expect(status), .expect_error(status, message), .body)
lib/utils.py           unique names and the create_user setup helper
lib/assertion.py       the only place with a bare `assert`; every check is logged
tests/api/             test_users.py, test_auth.py
```

what happens around a test:

- `reqres_clone` (session, automatic): uses the clone when `BASE_URL` answers, otherwise starts it and stops it after the run.
- `setup_session` (session, automatic): resets the services before the first and after the last test, only when `RESET_SERVICES=1`.
- `api` gives an `ApiClient` with `api.users_client` and `api.auth_client`.
- `testdata` carries the values from `constant_data` as attributes (`testdata.existing_user_id`, `testdata.login_email`) plus a unique user name per test, and `testdata.create_user()` makes a user for the test and returns its id. every test makes its own data, so no test depends on another.
- `response.expect(200)` checks the status and returns the response for chaining, the failure message carries the body.
- `response.expect_error(400, "Missing password")` checks the status and the `{"error": "..."}` message. if your api answers errors differently, change it in `lib/api/base.py` only.

## how to add a test

example: `GET /api/unknown/2` (a color) answers 200 with a name. the pattern is the existing user lookup, `get_user`.

1. value: put anything static in `constant_data` in `lib/constants.py` and expose it in `TestData` in `conftest.py` (copy a line, `self.x = constant_data["x"]`), so a test never types a magic value:

```python
# lib/constants.py, inside constant_data
"existing_color_id": 2,
"existing_color_name": "fuchsia rose",
```

2. path: add it to `lib/api/endpoints.py`, one class per service:

```python
class ColorsEndpoint:
    get_color = "/api/unknown/{color_id}"
```

3. call: add a client method in `lib/api/clients.py` (same shape as `UsersClient.get_user`), and one line in `ApiClient` in `conftest.py` (`self.colors_client = ColorsClient()`, plus the import):

```python
class ColorsClient(HttpClient):
    def __init__(self):
        super().__init__(environment_data["base_url"])

    def get_color(self, color_id):
        return self.get(ColorsEndpoint.get_color.format(color_id=color_id))
```

4. test: add a function in `tests/api/` (a new `test_colors.py` or an existing file), asking for the fixtures it needs. the existing one it copies, from `tests/api/test_users.py`:

```python
def test_getting_existing_user_returns_that_user(testdata, api, assertion):
    response = api.users_client.get_user(testdata.existing_user_id)
    user = response.expect(200).body["data"]
    assertion.assert_equal(
        actual_result=user["email"],
        expected_result=testdata.existing_user_email,
        label="user email",
    )
```

   several cases of one rule go in one `@pytest.mark.parametrize` table, see `test_auth_without_password_is_refused` in `tests/api/test_auth.py`.
5. run just that test, then the checks:

```bash
./run_test.sh tests/api/test_colors.py
./checks.sh
```

a second service is a new url in `environment_data` (and `test.env`), a new endpoint class, a new client class, and one line in `ApiClient`.

## docker (optional)

set `RUN_MODE="docker"` in `run_test.sh` and run it as usual. it builds the image from `Dockerfile` (python version from `.python-version`, packages from `requirements.pip`) and runs the `tests` service of `docker-compose.yml`; the report appears in `reports/` and `test.env` is mounted, so changing it needs no rebuild. do not start the compose file by hand, `run_test.sh` fills in `PYTHON_VERSION`. the clone runs on your host, so the container must reach it: `docker-compose.yml` has a commented `network_mode: host` line for Linux; Docker Desktop on Mac or Windows needs `BASE_URL` pointed at `host.docker.internal`. the docker run was not verified for this README.

## if it breaks

| symptom | cause | fix |
|---|---|---|
| `python3.8 not found, install Python 3.8.2 first` | `first_setup.sh` needs the 3.8 line | install Python 3.8, or make `python3` point to it |
| `No .venv yet, run ./first_setup.sh once first` | setup not done | run `./first_setup.sh` |
| `nothing on http://localhost:40000 and no clone at ...` | the clone is not running and not next to this repo | start it (quick start step 1) or set `REQRESIN_CLONE_DIR` in `test.env` |
| `the reqresin clone did not answer within 15 seconds` | the port is taken, or Python cannot start `server.py` | run `python3 server.py` in the clone folder by hand and read its error |
| `ConnectionError` / `Max retries exceeded` | nothing on `BASE_URL`, or the wrong port | `curl http://localhost:40000/api/users/2` should answer; fix `BASE_URL` |
| `HTTP status: actual 404 is not equal to expected 200` | wrong path, usually a missing `/api` | paths in `endpoints.py` start with `/api` |
| `NotImplementedError: no reset endpoint known` | `RESET_SERVICES=1` against reqres | set it back to `0` |
| `checks.sh` fails in black or pylint | style finding in new code | `.venv/bin/black .`, then fix what pylint lists |

debugging many failures: reproduce one failing call as a small standalone snippet (or `curl`), fix it, re-run only that test, and run the whole suite last.

## next

- the same layout for the browser: https://github.com/ClasherGeek77/pytest_web_boilerplate
- the target you just ran against: https://github.com/ClasherGeek77/reqresin_clone
- put a recording proxy in front of an api: https://github.com/ClasherGeek77/mock_proxy_django
- load tests with Locust: https://github.com/ClasherGeek77/locust_boilerplate
