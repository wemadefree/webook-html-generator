import datetime
from pydantic import BaseModel


class Person(BaseModel):
    personalEmail: str
    firstName: str
    middleName: str
    lastName: str
    birthDate: datetime.datetime