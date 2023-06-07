from pydantic import BaseModel,validator,root_validator
from config.constant import DEFAULT_AVATAR_MAN, LOCAL_PROVIDER, GOOGLE_PROVIDER, FACEBOOK_PROVIDER, MALE
from datetime import datetime

class UserRegisterDto(BaseModel):
    username :str
    email:str
    full_name:str
    avatar_url:str
    password:str

    @validator("avatar_url", pre=False)
    def setting_avatar_ur(cls, value):
        if value:
            return value
        return DEFAULT_AVATAR_MAN
    

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['role'] = 1
        data['sex'] = MALE
        data["provider"] = LOCAL_PROVIDER
        data["created_at"] = datetime.now().strftime("%Y-%m-%d %X")
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return data

class UserLoginDto(BaseModel):
    username :str
    password:str

class GoogleLogin(BaseModel):
    username :str
    email:str
    full_name:str
    avatar_url:str
    access_token: str

    @validator("avatar_url", pre=False)
    def default_avatar_ur(cls, value):
        if value:
            return value
        return DEFAULT_AVATAR_MAN
    
    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['role'] = 0
        data['sex'] = MALE
        data["provider"] = GOOGLE_PROVIDER
        data["password"] = ""
        data["created_at"] = datetime.now().strftime("%Y-%m-%d %X")
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return data
    
class FacabookLogin(BaseModel):
    username :str
    email:str
    full_name:str
    avatar_url:str
    access_token: str

    @validator("avatar_url", pre=False)
    def default_avatar_ur(cls, value):
        if value:
            return value
        return DEFAULT_AVATAR_MAN

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['role'] = 0
        data['sex'] = MALE
        data["provider"] = FACEBOOK_PROVIDER
        data["password"] = ""
        data["created_at"] = datetime.now().strftime("%Y-%m-%d %X")
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return data

