from pydantic import BaseModel,root_validator, validator
from datetime import datetime
from bson import ObjectId

class NotificationModel(BaseModel):
    mess : str =""
    ebook_id: str = ""
    post_id:str = ""
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")
    
    @validator("ebook_id", pre=False)
    def ebook_id_to_object(cls, value):
        try:
            if value and isinstance(value, str):
                value = ObjectId(value)
                return value
            return value
        except:
            return value
        
    @validator("post_id", pre=False)
    def post_id_to_object(cls, value):
        try:
            if value and isinstance(value, str):
                value = ObjectId(value)
                return value
            return value
        except:
            return value
        
    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values
    

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        return data
    
    