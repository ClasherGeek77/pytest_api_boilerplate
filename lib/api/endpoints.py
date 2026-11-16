# one class per service, endpoint names match the client method that uses them
class UsersEndpoint:
    list_users = "/api/users"
    get_user = "/api/users/{user_id}"
    create_user = "/api/users"
    update_user = "/api/users/{user_id}"
    delete_user = "/api/users/{user_id}"


class AuthEndpoint:
    login = "/api/login"
    register = "/api/register"
