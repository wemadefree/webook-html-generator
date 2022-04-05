import os


class Config:
    def __init__(self):
        self.base_url = os.getenv('BASE_URL')
        self.login_url = os.getenv('LOGIN_URL')
        self.user_name = os.getenv('USER_NAME')
        self.password = os.getenv('PASSWORD')
        self.default_request_time = os.getenv('DEFAULT_REQUESTS_TIMEOUT')
        self.events_url = os.getenv('EVENTS_URL')
        self.layout_url = os.getenv('LAYOUT_URL')
        self.scheduler_interval_in_sec = os.getenv('SCHEDULER_INTERVAL_SEC')
        self.scheduler_interval_in_min = os.getenv('SCHEDULER_INTERVAL_MIN')


