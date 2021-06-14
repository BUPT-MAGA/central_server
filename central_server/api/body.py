from pydantic import BaseModel


class CheckReq(BaseModel):
    room_id: str
    user_id: str


class AdminReq(BaseModel):
    username: str
    password: str
