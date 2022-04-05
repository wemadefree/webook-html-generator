import datetime
from common import CamelCaseMixin
from typing import List, Optional
from pydantic import BaseModel, EmailStr


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
    name: str
    max_capacity: int
    has_screen: bool
    location: Optional[Location]


class LayoutSetting(CamelCaseMixin):
    name: str
    html_template: str
    css_template: str
    file_output_path: str


class ScreenResource(CamelCaseMixin):
    name: str
    name_en: Optional[str]
    quantity: int
    is_room_screen: bool
    location_id: Optional[int]


class ScreenGroup(CamelCaseMixin):
    group_name: str
    group_name_en: Optional[str]
    quantity: int
    screens:  Optional[List[ScreenResource]]


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
    name: str
    name_en: Optional[str]
    icon_class: str


class ArrangementType(CamelCaseMixin):
    id: Optional[int]
    name: str
    name_en: Optional[str]


class Arrangement(CamelCaseMixin):
    id: int
    name: str
    name_en: Optional[str]
    starts: datetime.date
    ends: datetime.date
    audience: Optional[Audience]
    display_layouts: Optional[List[DisplayLayoutName]]
    arrangement_type: Optional[ArrangementType]


class Event(CamelCaseMixin):
    id: int
    title: str
    title_en: Optional[str]
    start: datetime.datetime
    end: datetime.datetime
    all_day: bool
    arrangement: Arrangement
    display_layouts: Optional[List[DisplayLayoutName]]
    rooms: Optional[List[Room]]


class DisplayData(CamelCaseMixin):
    starting_soon: str = ""
    event_time: str = ""
    arrangement_name: str = ""
    audience_name: str = ""
    audience_icon: str = ""
    arrangement_type_name: str = ""
    room_name: str = ""


class DisplayCombo(CamelCaseMixin):
    title: str
    css_path: Optional[str]
    data: List[DisplayData]







