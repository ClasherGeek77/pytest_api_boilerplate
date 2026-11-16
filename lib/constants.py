import os

_project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# dynamic, changes between runs or environments
# a second service gets its own url here, like "orders_url"
environment_data = {
    # the local reqresin clone, ../reqresin_clone/server.py, see README
    "base_url": os.environ.get("BASE_URL", "http://localhost:40000"),
    "timeout": int(os.environ.get("API_TIMEOUT", "10")),  # seconds per request
    "reset_services": os.environ.get("RESET_SERVICES", "0") == "1",
    # where the clone lives, only needed when BASE_URL answers nothing
    "clone_dir": os.path.abspath(
        os.environ.get(
            "REQRESIN_CLONE_DIR", os.path.join(_project_dir, "..", "reqresin_clone")
        )
    ),
}

# static, never changes between runs or environments
constant_data = {
    "existing_user_id": 2,
    "existing_user_email": "janet.weaver@reqres.in",
    "existing_user_first_name": "Janet",
    "unknown_user_id": 23,
    "page_size": 6,
    "total_users": 12,
    "user_fields": ["avatar", "email", "first_name", "id", "last_name"],
    "new_user_job": "leader",
    "updated_user_job": "zion resident",
    "login_email": "eve.holt@reqres.in",
    "login_password": "cityslicka",
    "register_password": "pistol",
    "registered_user_id": "4",
}
