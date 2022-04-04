import datetime
import json
import requests
import jinja2
from typing import List
from collections import defaultdict
from webook_html_generator.schema import DisplayLayout, Login, Token, Event, DisplayData, DisplayCombo
from webook_html_generator.config import Config


class Generator:
    def __init__(self, config: Config):
        self.token: Token = None
        self.layouts: List[DisplayLayout] = None
        self.config: Config = config
        self.initialize()

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

    def initialize(self):
        self.token: Token = self._get_token()
        self.layouts: List[DisplayLayout] = self._get_display_layouts()

    def _get_display_layouts(self) -> List[DisplayLayout]:
        """Returns the display settings for a request"""
        try:
            req = requests.get(self.config.layout_url)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Login Error:", err)
            return None
        setting_dict = json.loads(req.content)
        print(setting_dict)
        settings: List[DisplayLayout] = []
        for sett in setting_dict:
            settings.append(DisplayLayout(**sett))
        return settings

    def _get_next_events(self, location_name: str) -> List[Event]:
        try:
            req = requests.get(self.config.events_url)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Login Error:", err)
            return None
        event_dict = json.loads(req.content)
        print(event_dict)
        events: List[Event] = []
        for ev in event_dict:
            events.append(Event(**ev))
        return events

    def convert_to_display_data(self, event: Event, room_name: str = "", international: bool = False):
        display_data = DisplayData()
        if event.arrangement.audience:
            display_data.audience_icon = event.arrangement.audience.icon_class
        display_data.room_name = room_name

        days_in_no = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
        start_time = event.start.strftime("%H.%M")
        end_time = event.end.strftime("%H.%M")
        current_day_no = days_in_no[event.start.weekday()]
        current_day_en = event.start.strftime('%A')
        if event.start.date() == datetime.date.today():
            display_data.event_time = "{0}-{1}".format(start_time, end_time)
        else:
            if international:
                display_data.event_time = "{0} {1}-{2}".format(current_day_en, start_time, end_time)
            else:
                display_data.event_time = "{0} {1}-{2}".format(current_day_no, start_time, end_time)

        now = datetime.datetime.now()
        in_half_hour = datetime.datetime.now() + datetime.timedelta(minutes=530)

        if not international:
            if event.start >now and event.start < in_half_hour:
                display_data.starting_soon = "Starter snart"
            display_data.arrangement_name = event.arrangement.name
            if event.arrangement.audience:
                display_data.audience_name = event.arrangement.audience.name
            display_data.arrangement_type_name = event.arrangement.arrangement_type.name
        else:
            if event.start > now and event.start < in_half_hour:
                display_data.starting_soon = "Starting soon"
            display_data.arrangement_name = event.arrangement.name_en
            if event.arrangement.audience:
                display_data.audience_name = event.arrangement.audience.name_en
            display_data.arrangement_type_name = event.arrangement.arrangement_type.name_en

        return display_data

    def render_html(self, all_events: List[Event]):
        showcase_dict = self.arrange_display_data(all_events)
        for key in showcase_dict:
            print(showcase_dict[key])
            with open(f'template/whatson.html', 'r', encoding="utf-8") as f:
                contents = f.read()
            template = jinja2.Template(contents)
            display = DisplayCombo(title=key, data=showcase_dict[key])
            context = {
                'now': datetime.datetime.now(),
                'in_half_hour': datetime.datetime.now()+datetime.timedelta(minutes=30),
            }

            filled_template = template.render(display=display, **context)
            with open(f'html/whatson/{self._rename(key)}.html', 'w', encoding="utf-8") as f:
                f.write(filled_template)

    def _rename(self, name):
        words = name.split(" ")
        words_lower = [word.lower().replace(",", "").replace(".", "") for word in words]
        return "_".join(words_lower)

    def arrange_display_data(self, all_events: List[Event]) -> defaultdict:
        screen_showcase = defaultdict(list)
        for layout in self.layouts:
            if layout.room_based:
                for screen in layout.screens:
                    screen_showcase[screen.name] = []
                for group in layout.groups:
                    screen_showcase[group.group_name] = []
            else:
                screen_showcase[layout.name] = []

            regular_screen_names = [screen.name for screen in layout.screens]

            for event in all_events:
                arr_layout_names = [layout.name for layout in event.arrangement.display_layouts]
                evt_layout_names = [layout.name for layout in event.display_layouts]

                if layout.name in arr_layout_names and layout.name in evt_layout_names:
                    if layout.room_based:
                        for room in event.rooms:
                            for group in layout.groups:
                                for screen in group.screens:
                                    if screen.name == room.name:
                                        self._set_screen_showcase(screen_showcase[group.name], event, room_name=group.group_name)
                            if room.name in regular_screen_names:
                                self._set_screen_showcase(screen_showcase[room.name], event, room_name=room.name)
                    else:
                        if event.rooms:
                            room_names = [room.name for room in event.rooms]
                            self._set_screen_showcase(screen_showcase[layout.name], event, room_name=",".join(room_names))

        return screen_showcase

    def _set_screen_showcase(self, screen_showcase: List, event: Event, room_name: str = ""):
        if event.arrangement.name:
            screen_showcase.append(self.convert_to_display_data(event, room_name=room_name))
        if event.arrangement.name_en:
            screen_showcase.append(self.convert_to_display_data(event, room_name=room_name, international=True))

    def make_templates(self):
        events = self._get_next_events("")
        print(events)
        self.render_html(events)








