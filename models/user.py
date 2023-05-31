from pydantic import BaseModel,root_validator
from datetime import datetime

class User(BaseModel):
    username :str
    full_name:str
    email:str
    address :str
    phone:str
    intro:str
    profile:str
    password:str
    role:int
    avatar_url:str
    deleted_flag :bool
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now()
        return values