import datetime
from typing import List, Optional

import pytz
from pydantic import BaseModel, EmailStr, constr

from webook_html_generator.common import CamelCaseMixin

utc = pytz.UTC


class EventDisplayConfig(CamelCaseMixin):
    display_name: str
    display_type: str
    room_filter: List[str]
    output_file_name: bool
    location_id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class Login(BaseModel):
    username: EmailStr
    password: str


class Location(CamelCaseMixin):
    id: int
    name: str


class Room(CamelCaseMixin):
    id: int
    name: constr(strip_whitespace=True)
    name_en: Optional[constr(strip_whitespace=True)]
    max_capacity: int
    has_screen: bool
    location_id: Optional[int]
    location: Optional[Location]


class LayoutSetting(CamelCaseMixin):
    name: str
    html_template: str
    css_template: str
    file_output_path: str


class ScreenResource(CamelCaseMixin):
    screen_model: str
    items_shown: Optional[str]
    room_id: int
    room: Optional[Room]


class ScreenGroup(CamelCaseMixin):
    group_name: str
    group_name_en: Optional[str]
    quantity: int
    screens: Optional[List[ScreenResource]]


class DisplayLayout(CamelCaseMixin):
    name: str
    is_room_based: bool
    is_active: bool
    all_events: bool
    setting: Optional[LayoutSetting]
    screens: Optional[List[ScreenResource]]
    groups: Optional[List[ScreenGroup]]


class DisplayLayoutName(CamelCaseMixin):
    name: str


class Audience(CamelCaseMixin):
    id: int
    name: constr(strip_whitespace=True)
    name_en: Optional[constr(strip_whitespace=True)]
    icon_class: str


class ArrangementType(CamelCaseMixin):
    id: Optional[int]
    name: str
    name_en: Optional[str]


class Arrangement(CamelCaseMixin):
    id: int
    name: constr(strip_whitespace=True)
    name_en: Optional[constr(strip_whitespace=True)]
    starts: Optional[datetime.date]
    ends: Optional[datetime.date]
    meeting_place: Optional[constr(strip_whitespace=True)]
    meeting_place_en: Optional[constr(strip_whitespace=True)]
    audience: Optional[Audience]
    display_layouts: Optional[List[DisplayLayoutName]]
    arrangement_type: Optional[ArrangementType]
    location_id: Optional[int]
    location: Optional[Location]


class Event(CamelCaseMixin):
    id: int
    title: constr(strip_whitespace=True)
    title_en: Optional[constr(strip_whitespace=True)]
    start: datetime.datetime
    end: datetime.datetime
    all_day: bool
    arrangement: Arrangement
    display_text: Optional[constr(strip_whitespace=True)]
    display_text_en: Optional[constr(strip_whitespace=True)]
    display_layouts: Optional[List[DisplayLayoutName]]
    rooms: Optional[List[Room]]
    arrangement_type: Optional[ArrangementType]
    audience: Optional[Audience]


days_in_no = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
month_in_no = [
    "",
    "januar",
    "februar",
    "mars",
    "april",
    "mai",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "desember",
]


class DisplayData(CamelCaseMixin):
    event_time: str = ""
    arrangement_name: str = ""
    audience_name: str = ""
    audience_icon: str = ""
    arrangement_type_name: str = ""
    room_name: Optional[str] = ""
    international: bool = False
    starting_soon: str = ""

    def _set_time(self, event: Event, international: bool):
        local_start_time: datetime.datetime = event.start.astimezone(
            pytz.timezone("Europe/Oslo")
        )
        start_time: str = local_start_time.strftime("%H.%M")
        local_end_time: datetime.datetime = event.end.astimezone(
            pytz.timezone("Europe/Oslo")
        )
        end_time: str = local_end_time.strftime("%H.%M")
        current_day_no: str = days_in_no[event.start.weekday()]
        current_day_en: str = event.start.strftime("%A")
        if event.start.date() == datetime.date.today():
            self.event_time = "{0}-{1}".format(start_time, end_time)
        else:
            if international:
                self.event_time = "{0} {1}-{2}".format(
                    current_day_en, start_time, end_time
                )
            else:
                self.event_time = "{0} {1}-{2}".format(
                    current_day_no, start_time, end_time
                )

    def set_fields(
        self, event: Event, room_name: str = "", international: bool = False
    ):
        self.room_name = room_name
        self._set_time(event, international)
        self.international = international

        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        starting_soon_period = now + datetime.timedelta(minutes=60)

        if not international:
            if event.start > now and event.start < starting_soon_period:
                self.starting_soon = "Starter snart"
            if event.title:
                self.arrangement_name = event.title
            elif event.display_text:
                self.arrangement_name = event.display_text

            if event.audience:
                self.audience_name = event.audience.name
                self.audience_icon = event.audience.icon_class
            elif event.arrangement.audience:
                self.audience_name = event.arrangement.audience.name
                self.audience_icon = event.arrangement.audience.icon_class
            if event.arrangement_type:
                self.arrangement_type_name = event.arrangement_type.name
            else:
                self.arrangement_type_name = event.arrangement.arrangement_type.name
        else:
            if event.start > now and event.start < starting_soon_period:
                self.starting_soon = "Starting soon"
            if event.title_en:
                self.arrangement_name = event.title_en
            elif event.display_text_en:
                self.arrangement_name = event.display_text_en

            if event.audience:
                self.audience_name = event.audience.name_en
                self.audience_icon = event.audience.icon_class
            else:
                self.audience_name = event.arrangement.audience.name_en
                self.audience_icon = event.arrangement.audience.icon_class
            if event.arrangement_type:
                self.arrangement_type_name = event.arrangement_type.name_en
            else:
                self.arrangement_type_name = event.arrangement.arrangement_type.name_en


class DisplayCombo(CamelCaseMixin):
    title: str
    css_path: Optional[str] = ""
    data: List[DisplayData]
