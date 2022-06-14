import datetime

from pydantic import BaseModel, HttpUrl


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True
        json_encoders = {
            datetime.time: lambda v: v.strftime("%H:%M"),
        }


class UrlCreate(BaseSchema):
    url: HttpUrl


class Url(BaseSchema):
    url_short: str


class StatsResponse(BaseModel):
    redirects_in_24_hours: int
