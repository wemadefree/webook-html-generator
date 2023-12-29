import os


class Config:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL")
        self.login_url = os.getenv("LOGIN_URL")
        self.user_name = os.getenv("USER_NAME")
        self.password = os.getenv("PASSWORD")
        self.default_request_time = os.getenv("DEFAULT_REQUESTS_TIMEOUT")
        self.next_events_url = os.getenv(
            "NEXT_EVENTS_URL", "events/next_on_schedule?days_ahead=6&limit=1000"
        )
        self.current_events_url = os.getenv("CURRENT_EVENTS_URL", "events/current")
        self.screens_url = os.getenv(
            "SCREENS_URL", "screenresources?offset=0&limit=100"
        )
        self.rooms_url = os.getenv("ROOMS_URL", "rooms?offset=0&limit=100")
        self.locations_url = os.getenv("LOCATIONS_URL", "locations?offset=0&limit=100")
        self.layout_url = os.getenv("LAYOUT_URL", "displaylayouts?offset=0&limit=100")
        self.scheduler_interval_in_sec = os.getenv("SCHEDULER_INTERVAL_SEC")
        self.scheduler_interval_in_min = os.getenv("SCHEDULER_INTERVAL_MIN")
        self.upload_dir = os.getenv("UPLOAD_DIR")
        self.mmg_dir = os.getenv("MMG_DIR")
        self.max_screen_items = os.getenv("MAX_SCREEN_ITEMS")

        self.google_cloud_sync = os.getenv("GOOGLE_CLOUD_SYNC")
        self.google_cloud_bucket = os.getenv("GOOGLE_CLOUD_BUCKET")

        self.api_code = os.getenv("API_CODE")
        self.produce_swagger = os.getenv("PRODUCE_SWAGGER", True)
