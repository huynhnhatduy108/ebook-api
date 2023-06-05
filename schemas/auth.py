from pydantic import BaseModel
from config.constant import LOCAL_PROVIDER

class UserRegisterDto(BaseModel):
    username :str
    email:str
    full_name:str
    password:str

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['role'] = 1
        data["provider"] = LOCAL_PROVIDER
        return data

class UserLoginDto(BaseModel):
    username :str
    password:str
