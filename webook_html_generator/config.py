import os


class Config:
    def __init__(self):
        self.base_url = os.getenv('BASE_URL')
        self.login_url = os.getenv('LOGIN_URL')
        self.user_name = os.getenv('USER_NAME')
        self.password = os.getenv('PASSWORD')
        self.default_request_time = os.getenv('DEFAULT_REQUESTS_TIMEOUT')
        self.next_events_url = os.getenv('NEXT_EVENTS_URL')
        self.current_events_url = os.getenv('CURRENT_EVENTS_URL')
        self.screens_url = os.getenv('SCREEN_URL')
        self.rooms_url = os.getenv('ROOM_URL')
        self.locations_url = os.getenv('LOCATION_URL')
        self.layout_url = os.getenv('LAYOUT_URL')
        self.scheduler_interval_in_sec = os.getenv('SCHEDULER_INTERVAL_SEC')
        self.scheduler_interval_in_min = os.getenv('SCHEDULER_INTERVAL_MIN')
        self.upload_dir = os.getenv('UPLOAD_DIR')
        self.mmg_dir = os.getenv('MMG_DIR')
        self.max_screen_items = os.getenv('MAX_SCREEN_ITEMS')


