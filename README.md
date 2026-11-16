# pytest autotest boilerplate

a starter for api autotests with python and pytest. the example target is the local **reqresin clone** in `../reqresin_clone` (http://localhost:40000), a byte-faithful stdlib server of https://reqres.in. no internet, no rate limits, no daily quota. made on 2026-10-03, pointed at the local clone on 2026-11-16.

## how to run it

```bash
./first_setup.sh          # once, builds .venv from requirements.pip
./run_test.sh             # all tests
./run_test.sh tests/api/  # all api tests
./run_test.sh tests/api/test_users.py::test_deleting_user_returns_no_content  # one test
./checks.sh               # bandit, black and pylint
```

nobody needs to remember any pytest cli syntax. `run_test.sh` has three settings at the top, with the example of each variant in a comment:

- `TEST_PATH`: what runs by default. an argument replaces it.
- `REPORT_NAME`: default is `reports/report_<timestamp>_<test path>.html`.
- `RUN_MODE`: `"local"` runs on this machine with `.venv`, `"docker"` runs inside docker. the same script, the same tests, the same report.

settings of the services are plain `KEY=value` lines in `test.env`. every setting is shown at the start of each run.

## the clone and how it comes up

- normally nothing to do: the clone answers on `BASE_URL` already (start it by hand with `python3 ../reqresin_clone/server.py`, or let this machine's `clone-guard` keep it up).
- if nothing answers, the test session starts `server.py` itself from `REQRESIN_CLONE_DIR` (default `../reqresin_clone`) and stops it again after the run. the clone is stdlib-only python, so the venv's own python can run it.

## folders

- `tests/api/`: the tests. a test asks for the fixtures it needs, no import needed.
- `lib/`: everything a test uses.
  - `api/base.py`: `HttpClient` (get, post, put, delete, one place that logs every request and reply) and `ApiResponse` (`.expect(status)`, `.expect_error(status, message)`, `.body`).
  - `api/endpoints.py`: the paths, one class per service.
  - `api/clients.py`: one class per service, every method is one or two lines that call get or post.
  - `constants.py`: `constant_data` for static data, `environment_data` for what comes from `test.env`.
  - `utils.py`: unique names and setup helpers.
  - `assertion.py`: the only place with a bare `assert`, every check is logged as a step.
- `conftest.py`: the fixtures `reqres_clone`, `api`, `testdata`, `assertion` and `logger`.
- `Dockerfile` and `docker-compose.yml`: the docker run.

## a new api test in minutes

1. a static value goes in `constant_data`, and `testdata` brings it, so the test never types a magic value.
2. a new path goes in `lib/api/endpoints.py`.
3. a new call is a client method in `lib/api/clients.py`:

```python
def get_user(self, user_id):
    return self.get(UsersEndpoint.get_user.format(user_id=user_id))
```

4. the test, with `logger.warning(...)` lines in it when it has several steps:

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

a second service is a new url in `environment_data`, a new endpoint class and a new client class, then one line in `ApiClient` in `conftest.py`.

## independence and setup

- every test makes its own data with a unique name, so a test does not depend on what another test made.
- `setup_session` in `conftest.py` runs once before the first test and once after the last, not for every test. it only runs when `RESET_SERVICES=1`.
- reqres has no reset endpoint, so `RESET_SERVICES` is 0 here and `ApiClient.reset_all` raises an error on purpose. for a service that has a reset endpoint, call it there.

## docker

set `RUN_MODE="docker"` in `run_test.sh`, then run it as usual. it builds the image from `Dockerfile`, then starts the `tests` service of `docker-compose.yml`. an argument still replaces the test path, like `./run_test.sh tests/api/`.

- the python version comes from `.python-version` and the packages from `requirements.pip`, so there is one place to change each.
- the report appears in `reports/` on your machine, and `test.env` is mounted, so a change in it needs no rebuild.
- a change in the tests or `lib/` is picked up by the build at the start of the run, quick because the slow package layer is reused.
- do not start the compose file by hand, `PYTHON_VERSION` is filled in by `run_test.sh` and the build stops with a message without it.
- the target is a clone on `localhost`, and `localhost` inside a container is not `localhost` on the mac. docker mode is untested on this machine; on linux `network_mode: host` in the compose file makes it work, on mac give the clone a routable address and set `BASE_URL` to it.

## about the local clone as the example target

- the same read-only contract as reqres.in: `POST /api/users` answers an id, but nothing is stored, so a get after it never finds that user. the api tests check each reply on its own for that reason.
- no rate limit at all, run it as often as you like.
- `POST /api/register` answers `{"id": "4", "token": ...}` and `POST /api/users` answers id `"4"`, pinned like live reqres.
- errors come as `{"error": "message"}`. if your api has another shape, change `expect_error` in `lib/api/base.py` only.
- for a real practice, point `BASE_URL` in `test.env` to your own service and change `constant_data`, the endpoints and the clients.

## lint

Bandit, black and pylint. no lint plugins. `.python-version` and every package in `requirements.pip` are pinned.

## left out on purpose

a ci pipeline, parallel runs and load tests. the browser tests that used to hit the real reqres.in website are gone: this project is api-only now, and web automation lives in `../pytest_boilerplate_web` against the local saucedemo clone.
