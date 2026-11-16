import logging
import os
import subprocess  # nosec B404
import sys
import time
from urllib.parse import urlparse

import pytest
import requests

from lib.assertion import Assertion
from lib.api.clients import AuthClient, UsersClient
from lib.constants import constant_data, environment_data
from lib.utils import create_user, unique_user_name

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self):
        self.users_client = UsersClient()
        self.auth_client = AuthClient()

    # this demo api has no reset endpoint, so RESET_SERVICES stays 0
    # for a service that has one, call it here, like
    # self.users_client.reset().expect(204)
    def reset_all(self):
        raise NotImplementedError(
            "no reset endpoint known, fill in ApiClient.reset_all"
        )


class TestData:
    def __init__(self, api):
        self.api = api
        self.user_name = unique_user_name()
        self.user_job = constant_data["new_user_job"]
        self.updated_user_job = constant_data["updated_user_job"]
        self.existing_user_id = constant_data["existing_user_id"]
        self.existing_user_email = constant_data["existing_user_email"]
        self.existing_user_first_name = constant_data["existing_user_first_name"]
        self.unknown_user_id = constant_data["unknown_user_id"]
        self.page_size = constant_data["page_size"]
        self.total_users = constant_data["total_users"]
        self.user_fields = constant_data["user_fields"]
        self.login_email = constant_data["login_email"]
        self.login_password = constant_data["login_password"]
        self.register_password = constant_data["register_password"]
        self.registered_user_id = constant_data["registered_user_id"]

    # a user for this test, returns the id
    def create_user(self):
        return create_user(self.api.users_client, self.user_name, self.user_job)


def clone_is_up():
    try:
        requests.get(environment_data["base_url"] + "/api", timeout=2)
        return True
    except requests.RequestException:
        return False


# the reqresin clone normally runs on its own (see README), but when nothing
# answers the session starts it from REQRESIN_CLONE_DIR and stops it again
@pytest.fixture(autouse=True, scope="session")
def reqres_clone():
    if clone_is_up():
        logger.info(f"reqresin clone is answering on {environment_data['base_url']}")
        yield
        return
    clone_dir = environment_data["clone_dir"]
    if not os.path.isdir(clone_dir):
        raise RuntimeError(
            f"nothing on {environment_data['base_url']} and no clone at {clone_dir}, "
            "start the server or fix REQRESIN_CLONE_DIR in test.env"
        )
    port = urlparse(environment_data["base_url"]).port or 40000
    logger.info(f"starting the reqresin clone from {clone_dir} on port {port}")
    # one local dev server with fixed arguments, nothing from user input
    # the process must outlive this line, the yield and terminate end it
    process = subprocess.Popen(  # pylint: disable=consider-using-with  # nosec B603
        [sys.executable, "server.py", "--port", str(port)],
        cwd=clone_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 15
    while time.time() < deadline and not clone_is_up():
        time.sleep(0.3)
    if not clone_is_up():
        process.terminate()
        raise RuntimeError("the reqresin clone did not answer within 15 seconds")
    yield
    process.terminate()
    process.wait(timeout=10)


# runs once before the first test and once after the last test
@pytest.fixture(autouse=True, scope="session")
def setup_session():
    if environment_data["reset_services"]:
        logger.info("setting up, resetting the services before the first test")
        ApiClient().reset_all()

    yield

    if environment_data["reset_services"]:
        logger.info("tearing down, resetting the services after the last test")
        ApiClient().reset_all()


@pytest.fixture
def api():
    return ApiClient()


@pytest.fixture
def testdata(api):
    return TestData(api)


@pytest.fixture
def assertion():
    return Assertion()


@pytest.fixture(name="logger")
def step_logger():
    return logging.getLogger("test")
