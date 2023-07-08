from pydantic import BaseModel,root_validator
from datetime import datetime

class Ads(BaseModel):
    name :str = ""
    width:int 
    height :int
    script :str = ""
    sponsor:str =""
    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values
    
    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        return data