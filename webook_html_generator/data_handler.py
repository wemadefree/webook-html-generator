import json
import requests
from typing import List
from webook_html_generator.schema import (
    DisplayLayout, Login, Token, Event, ScreenResource, Location, Room)
from webook_html_generator.config import Config


class DataHandler:

    def __init__(self, config: Config):
        self.config: Config = config
        self.token: Token = None
        self.layouts: List[DisplayLayout] = None
        self.screens: List[ScreenResource] = None
        self.rooms: List[Room] = None
        self.locations: List[Location] = None
        self.events: List[Event] = None
        self.initialize()

    def initialize(self):
        self._get_token()
        self.layouts: List[DisplayLayout] = self._get_display_layouts()
        self.screens: List[ScreenResource] = self._get_screens()
        self.locations: List[Location] = self._get_locations()
        self.events: List[Event] = self._get_next_events()
        self.rooms: List[Room] = self._get_rooms()

    def refresh_token(self):
        return self._get_token()

    def _get_token(self):
        """Returns the token for a request"""
        print(self.config.__dict__)
        login = Login(username=self.config.user_name, password=self.config.password)
        try:
            req = requests.post(self.config.login_url, data=login.__dict__)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Login Error:", err)
            self.token = None
        self.token = Token(**json.loads(req.content))

    def _make_request(self, url: str) -> requests.Response:
        """Returns the screenresources for a request"""
        try:
            screen_url = self.config.base_url + url
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.token.access_token)}
            print(headers)
            req = requests.get(screen_url, headers=headers)
            req.raise_for_status()
            return req
        except requests.exceptions.HTTPError as err:
            print("Http Login Error:", err)
            return None

    def _get_display_layouts(self) -> List[DisplayLayout]:
        """Returns the display settings for a request"""

        try:
            req: requests.Response = self._make_request(self.config.layout_url)
            setting_dict = json.loads(req.content)
            print(setting_dict)
            settings: List[DisplayLayout] = []
            for sett in setting_dict:
                settings.append(DisplayLayout(**sett))
            return settings
        except Exception as ex:
            print(ex)
            return None

    def _get_screens(self) -> List[ScreenResource]:
        """Returns the screenresources for a request"""
        try:
            req: requests.Response = self._make_request(self.config.screens_url)
            screen_dict = json.loads(req.content)
            screens: List[ScreenResource] = []
            for sett in screen_dict:
                screens.append(ScreenResource(**sett))
            return screens
        except Exception as ex:
            print(ex)
            return None

    def _get_rooms(self) -> List[Room]:
        """Returns the screenresources for a request"""
        try:
            req: requests.Response = self._make_request(self.config.rooms_url)
            room_dict = json.loads(req.content)
            rooms: List[Room] = []
            for sett in room_dict:
                rooms.append(Room(**sett))
            return rooms
        except Exception as ex:
            print(ex)
            return None

    def _get_next_events(self) -> List[Event]:
        """Returns the events for a request"""
        try:
            req: requests.Response = self._make_request(self.config.events_url)
            event_dict = json.loads(req.content)
            events: List[Event] = []
            for ev in event_dict:
                events.append(Event(**ev))
            return events
        except Exception as ex:
            print(ex)
            return None

    def _get_locations(self) -> List[Location]:
        """Returns the locations for a request"""
        try:
            req: requests.Response = self._make_request(self.config.locations_url)
            loc_dict = json.loads(req.content)
            locs: List[Location] = []
            for l in loc_dict:
                locs.append(Location(**l))
            return locs
        except Exception as ex:
            print(ex)
            return None
