import pytest


def test_login_with_valid_credentials_returns_a_token(testdata, api, assertion):
    response = api.auth_client.login(testdata.login_email, testdata.login_password)
    body = response.expect(200).body
    assertion.assert_not_empty(
        actual_result=body["token"],
        label="login token",
    )


def test_register_with_valid_credentials_returns_id_and_token(testdata, api, assertion):
    response = api.auth_client.register(
        testdata.login_email, testdata.register_password
    )
    body = response.expect(200).body
    assertion.assert_equal(
        actual_result=body["id"],
        expected_result=testdata.registered_user_id,
        label="registered id",
    )
    assertion.assert_not_empty(
        actual_result=body["token"],
        label="register token",
    )


# the data-driven pattern from the reference repo: one test, one table,
# one id per row, expectations still come from constants not the table


@pytest.mark.parametrize(
    ("call_name", "expected_error"),
    [("login", "Missing password"), ("register", "Missing password")],
    ids=["login", "register"],
)
def test_auth_without_password_is_refused(testdata, api, call_name, expected_error):
    call = getattr(api.auth_client, call_name)
    response = call(testdata.login_email)
    response.expect_error(400, expected_error)
