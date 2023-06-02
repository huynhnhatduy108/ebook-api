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
    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values