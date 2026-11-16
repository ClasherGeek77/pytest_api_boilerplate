def test_listing_users_returns_the_first_page_with_the_documented_fields(
    testdata,
    api,
    assertion,
    logger,
):
    response = api.users_client.list_users(page=1)
    body = response.expect(200).body
    assertion.assert_equal(
        actual_result=body["page"],
        expected_result=1,
        label="page",
    )
    assertion.assert_length(
        actual_array=body["data"],
        expected_length=testdata.page_size,
        label="users on the page",
    )
    assertion.assert_equal(
        actual_result=body["total"],
        expected_result=testdata.total_users,
        label="total",
    )

    logger.warning("checking the fields of the first listed user")
    first_user = body["data"][0]
    assertion.assert_equal(
        actual_result=sorted(first_user.keys()),
        expected_result=testdata.user_fields,
        label="user fields",
    )


def test_getting_existing_user_returns_that_user(testdata, api, assertion):
    response = api.users_client.get_user(testdata.existing_user_id)
    user = response.expect(200).body["data"]
    assertion.assert_equal(
        actual_result=user["id"],
        expected_result=testdata.existing_user_id,
        label="user id",
    )
    assertion.assert_equal(
        actual_result=user["email"],
        expected_result=testdata.existing_user_email,
        label="user email",
    )
    assertion.assert_equal(
        actual_result=user["first_name"],
        expected_result=testdata.existing_user_first_name,
        label="user first name",
    )


def test_getting_unknown_user_is_not_found(testdata, api, assertion):
    response = api.users_client.get_user(testdata.unknown_user_id)
    response.expect(404)
    assertion.assert_equal(
        actual_result=response.body,
        expected_result={},
        label="not found body",
    )


def test_creating_user_returns_the_sent_data_and_a_new_id(testdata, api, assertion):
    response = api.users_client.create_user(testdata.user_name, testdata.user_job)
    created = response.expect(201).body
    assertion.assert_equal(
        actual_result=created["name"],
        expected_result=testdata.user_name,
        label="created name",
    )
    assertion.assert_equal(
        actual_result=created["job"],
        expected_result=testdata.user_job,
        label="created job",
    )
    assertion.assert_not_empty(
        actual_result=created["id"],
        label="created id",
    )
    assertion.assert_not_empty(
        actual_result=created["createdAt"],
        label="created at",
    )


def test_updating_user_returns_the_new_job(testdata, api, assertion, logger):
    logger.warning("setting up, a user to update")
    user_id = testdata.create_user()

    response = api.users_client.update_user(
        user_id, testdata.user_name, testdata.updated_user_job
    )
    updated = response.expect(200).body
    assertion.assert_equal(
        actual_result=updated["job"],
        expected_result=testdata.updated_user_job,
        label="updated job",
    )
    assertion.assert_equal(
        actual_result=updated["name"],
        expected_result=testdata.user_name,
        label="updated name",
    )
    assertion.assert_not_empty(
        actual_result=updated["updatedAt"],
        label="updated at",
    )


def test_deleting_user_returns_no_content(testdata, api, assertion, logger):
    logger.warning("setting up, a user to delete")
    user_id = testdata.create_user()

    response = api.users_client.delete_user(user_id)
    response.expect(204)
    assertion.assert_equal(
        actual_result=response.body,
        expected_result="",
        label="delete body",
    )
