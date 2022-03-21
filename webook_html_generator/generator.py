import json
import requests
import jinja2
from typing import List
from collections import defaultdict
from webook_html_generator.schema import Arrangement, Login, Token, Event, DisplayData, Room, DisplayConfiguration, DisplayCombo
from webook_html_generator.config import Config


class Generator:
    def __init__(self, config: Config):
        self.config = config
        self.token = self._get_token()
        self.screen_settings = self._get_screen_settings()

    def _get_token(self) -> Token:
        """Returns the token for a request"""

        print(self.config.__dict__)
        login = Login(username=self.config.user_name, password=self.config.password)
        try:
            req = requests.post(self.config.login_url, data=login.__dict__)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Login Error:", err)
            return None
        return json.loads(req.content)

    def _get_screen_settings(self) -> List[DisplayConfiguration]:
        """Returns the diplay settings for a request"""
        try:
            req = requests.get('http://localhost:8440/api/v1/displayconfigs?offset=0&limit=100')
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Login Error:", err)
            return None
        setting_dict = json.loads(req.content)
        print(setting_dict)
        settings: List[DisplayConfiguration] = []
        for sett in setting_dict:
            settings.append(DisplayConfiguration(**sett))
        return settings

    def _get_next_events(self, location_name: str) -> List[Event]:
        try:
            req = requests.get('http://localhost:8440/api/v1/events/next_on_schedule')
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Login Error:", err)
            return None
        event_dict = json.loads(req.content)
        events: List[Event] = []
        for ev in event_dict:
            events.append(Event(**ev))
        return events

    def _get_rooms_per_location(self, location_id: int) -> List[str]:
        try:
            req = requests.get(f'http://localhost:8440/api/v1/rooms/{location_id}')
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Login Error:", err)
            return None
        room_dict = json.loads(req.content)
        room_names: List[str] = []
        for rm in room_dict:
            room_names.append(rm['name'])
        return room_names

    def _flatten_events(self, events: List[Event]):
        flatten_events: List[DisplayData] = []
        for event in events:
            for room in event.rooms:
                flatten = DisplayData(**event.dict())
                flatten.arrangement_name = event.arrangement.name
                flatten.show_in_mmg = event.arrangement.show_in_mmg
                flatten.show_on_welcome = event.arrangement.show_on_welcome
                flatten.show_on_screen = event.arrangement.show_on_screen
                flatten.audience_name = event.arrangement.audience.name
                flatten.room_name = room.name
                flatten.has_screen = room.has_screen
                flatten_events.append(flatten)
        return flatten_events

    def _flatten_event(self, event: Event, room_name: str = ""):
        flatten = DisplayData(**event.dict())
        flatten.arrangement_name = event.arrangement.name
        flatten.audience_name = event.arrangement.audience.name
        flatten.room_name = room_name
        flatten.audience_icon_class = event.arrangement.audience.icon_class
        flatten.arrangement_type_name = event.arrangement.arrangement_type.name

        return flatten

    def render_html(self, all_events: List[Event]):
        data_per_screen_dict = self.arrange_display_data_per_screen(all_events)
        for key in data_per_screen_dict:
            print(data_per_screen_dict[key])
            with open(f'template/whatson.html', 'r') as f:
                contents = f.read()
            template = jinja2.Template(contents)
            display = DisplayCombo(title=key, data=data_per_screen_dict[key])
            filled_template = template.render(display=display)
            with open(f'html/whatson/{key}.html', 'w') as f:
                f.write(filled_template)

    def arrange_display_data_per_screen(self, all_events: List[Event]) -> defaultdict:
        data_per_screen = defaultdict(list)
        for event in all_events:
            arrangement_display_names = [config.name for config in event.arrangement.display_configurations]
            for setting in self.screen_settings:
                if setting.name in arrangement_display_names and not setting.room_based:
                    data_per_screen[setting.name].append(self._flatten_event(event))
                elif setting.name in arrangement_display_names and setting.room_based:
                    if setting.config_detail:
                        room_names = [room.name for room in setting.config_detail.room_combo]
                        for room in event.rooms:
                            if room.name in room_names:
                                data_per_screen[setting.config_detail.name].append(self._flatten_event(event, setting.config_detail.name))
                            else:
                                data_per_screen[room.name].append(self._flatten_event(event, room_name=room.name))
        return data_per_screen

    def make_templates(self):
        events = self._get_next_events("")
        self.render_html(events)








