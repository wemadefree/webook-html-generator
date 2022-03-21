import os


class Config:
    def __init__(self):
        self.base_url = os.getenv('BASE_URL')
        self.login_url = os.getenv('LOGIN_URL')
        self.user_name = os.getenv('USER_NAME')
        self.password = os.getenv('PASSWORD')
        self.default_request_time = os.getenv('DEFAULT_REQUESTS_TIMEOUT')


