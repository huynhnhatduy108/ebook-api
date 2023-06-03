from pydantic import BaseModel,root_validator, validator, Field
from datetime import datetime
from bson import ObjectId
from functions.function import  gen_slug_radom_string

class Post(BaseModel):
    name: str =""
    categories: list[str] =[]
    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @validator("categories", pre=False)
    def convert_object_id(cls, value):
        if isinstance(value, list):
            return [ObjectId(v) if isinstance(v, str) else v for v in value]
        return value
    

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['slug'] = gen_slug_radom_string(self.name)
        data['categories'] = self.categories
        return data
    