import datetime
import enum
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


class DisplayDetail(CamelCaseMixin):
    id: int
    name: str
    quantity: int
    room_combo: Optional[List[Room]]


class DisplayConfiguration(CamelCaseMixin):
    id: int
    name: str
    description: str
    all_events: bool
    room_based: bool
    quantity: int
    config_detail: Optional[DisplayDetail]


class DisplayConfigurationName(CamelCaseMixin):
    name: str


class Audience(CamelCaseMixin):
    id: int
    name: str
    icon_class: str


class ArrangementType(CamelCaseMixin):
    id: Optional[int]
    name: str
    name_en: Optional[str]


class Arrangement(CamelCaseMixin):
    id: int
    name: str
    starts: datetime.date
    ends: datetime.date
    audience: Optional[Audience]
    display_configurations: Optional[List[DisplayConfigurationName]]
    arrangement_type: Optional[ArrangementType]


class Event(CamelCaseMixin):
    id: int
    title: str
    title_en: Optional[str]
    start: datetime.datetime
    end: datetime.datetime
    all_day: bool
    arrangement: Arrangement
    rooms: Optional[List[Room]]


class DisplayData(CamelCaseMixin):
    id: int
    start: datetime.datetime
    end: datetime.datetime
    all_day: bool
    arrangement_name: str = ""
    audience_name: str = ""
    audience_icon_class: str = ""
    arrangement_type_name: str = ""
    room_name: str = ""


class DisplayCombo(CamelCaseMixin):
    title: str
    css_path: Optional[str]
    data: List[DisplayData]




