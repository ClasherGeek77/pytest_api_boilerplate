import logging
import time

logger = logging.getLogger(__name__)

# last number handed out, so two ids made in the same millisecond still differ
last_number = {"value": 0}


# the timestamp keeps runs apart, the counter keeps ids apart inside a run
def unique_number():
    last_number["value"] = last_number["value"] + 1
    number = last_number["value"]
    timestamp = int(time.time() * 1000)
    return f"{timestamp}-{number}"


# if the api needs a number id, change this to return the timestamp only
def unique_user_name():
    return "autotest-" + unique_number()


# each step checks its status, so a bad setup fails here and not inside the test
def create_user(users_client, name, job):
    logger.info(f"setting up a user named {name}")
    created = users_client.create_user(name, job)
    created.expect(201)
    return created.body["id"]
