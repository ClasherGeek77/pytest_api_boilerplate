from lib.api.base import HttpClient
from lib.constants import environment_data
from lib.api.endpoints import AuthEndpoint, UsersEndpoint


# one client per service or area, every method is one or two lines
class UsersClient(HttpClient):
    def __init__(self):
        super().__init__(environment_data["base_url"])

    def list_users(self, page=1):
        return self.get(UsersEndpoint.list_users, params={"page": page})

    def get_user(self, user_id):
        return self.get(UsersEndpoint.get_user.format(user_id=user_id))

    def create_user(self, name, job):
        return self.post(UsersEndpoint.create_user, json={"name": name, "job": job})

    def update_user(self, user_id, name, job):
        return self.put(
            UsersEndpoint.update_user.format(user_id=user_id),
            json={"name": name, "job": job},
        )

    def delete_user(self, user_id):
        return self.delete(UsersEndpoint.delete_user.format(user_id=user_id))


# same base url as UsersClient here, a different service would use its own url
class AuthClient(HttpClient):
    def __init__(self):
        super().__init__(environment_data["base_url"])

    # password is optional so a test can leave it out
    def login(self, email, password=None):
        return self.post(AuthEndpoint.login, json=self._credentials(email, password))

    def register(self, email, password=None):
        return self.post(AuthEndpoint.register, json=self._credentials(email, password))

    def _credentials(self, email, password):
        credentials = {"email": email}
        if password is not None:
            credentials["password"] = password
        return credentials
