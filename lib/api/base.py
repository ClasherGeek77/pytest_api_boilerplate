import logging

import requests

from lib.assertion import Assertion
from lib.constants import environment_data

logger = logging.getLogger(__name__)


class ApiResponse:
    def __init__(self, http_response):
        self.assertion = Assertion()
        self.status_code = http_response.status_code
        content_type = http_response.headers.get("content-type", "")
        is_json = "application/json" in content_type
        # empty replies can still have a json content-type
        if is_json and http_response.content:
            self.body = http_response.json()
        else:
            self.body = http_response.text

    # failure message has the body, returns self so calls chain
    def expect(self, status_code):
        self.assertion.assert_status(self.status_code, status_code, f"body {self.body}")
        return self

    # this api answers errors as {"error": "message"}
    # if yours differs, change it here only
    def expect_error(self, status_code, error_message):
        self.expect(status_code)
        self.assertion.assert_equal(
            actual_result=self.body["error"],
            expected_result=error_message,
            label="error message",
            detail=self.body,
        )
        return self.body["error"]


# get, post, put and delete shared by every client
# a client method is just endpoint + payload
class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get(self, endpoint, params=None):
        return self._send("GET", endpoint, params=params)

    def post(self, endpoint, json=None, headers=None):
        return self._send("POST", endpoint, json, headers)

    def put(self, endpoint, json=None, headers=None):
        return self._send("PUT", endpoint, json, headers)

    def delete(self, endpoint):
        return self._send("DELETE", endpoint)

    def _send(self, method, endpoint, json=None, headers=None, params=None):
        url = self.base_url + endpoint
        message = f"sending {method} {url}"
        if params is not None:
            message = message + f", params {params}"
        if json is not None:
            message = message + f", body {json}"
        if headers is not None:
            message = message + f", headers {headers}"
        logger.info(message)

        http_response = self.session.request(
            method,
            url,
            params=params,
            json=json,
            headers=headers,
            timeout=environment_data["timeout"],
        )
        response = ApiResponse(http_response)

        if response.body:
            logger.info(f"got {response.status_code} back with {response.body}")
        else:
            logger.info(f"got {response.status_code} back with no body")
        return response
