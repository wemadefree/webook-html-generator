import datetime
import enum
from common import CamelCaseMixin
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class StageChoices(str, enum.Enum):
    PLANNING = 'planning'
    REQUISITIONING = 'requisitioning'
    READY_TO_LAUNCH = 'ready_to_launch'
    IN_PRODUCTION = 'in_production'


class Token(BaseModel):
    access_token: str
    token_type: str


class Login(BaseModel):
    username: EmailStr
    password: str


class Person(CamelCaseMixin):
    personal_email: EmailStr
    first_name: str
    middle_name: str
    last_name: str
    birth_date: datetime.date


class Note(CamelCaseMixin):
    id: int
    content: str
    author: Optional[Person]


class Audience(CamelCaseMixin):
    id: int
    name: str
    icon_class: str


class OrganizationType(CamelCaseMixin):
    id: int
    name: str


class Organization(CamelCaseMixin):
    name: str
    organization_number: int
    organization_type: Optional[OrganizationType]


class TimeLineEvent(CamelCaseMixin):
    id: int
    content: Optional[str]
    stamp: Optional[datetime.datetime]


class ArrangementBase(CamelCaseMixin):
    name: str
    stages: StageChoices
    starts: datetime.date
    ends: datetime.date


class ArrangementRead(ArrangementBase):
    id: int
    audience: Optional[Audience]
    responsible: Optional[Person]

    timeline_events: List[TimeLineEvent]
    planners: List[Person]
    people_participants: List[Person]
    organization_participants: List[Organization]
    notes: List[Note]