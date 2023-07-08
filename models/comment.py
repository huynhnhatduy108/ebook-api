from pydantic import BaseModel,root_validator, validator
from datetime import datetime
from bson import ObjectId


class EbookComment(BaseModel):
    ebook_id: str = ""
    parent_id:str = ""
    content:str = ""

    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @validator("ebook_id", pre=False)
    def ebook_id_convert_object_id(cls, value):
        if value and isinstance(value, str):
            return ObjectId(value)
        return value
    
    @validator("parent_id", pre=False)
    def parent_id_convert_object_id(cls, value):
        if value and isinstance(value, str):
            return ObjectId(value)
        return value

    @root_validator
    def number_validator(cls, values):
        values["created_at"] = datetime.now().strftime("%Y-%m-%d %X")
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        return data
    
class PostComment(BaseModel):
    post_id: str = ""
    parent_id:str = ""
    content:str = ""

    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @validator("post_id", pre=False)
    def ebook_id_convert_object_id(cls, value):
        if value and isinstance(value, str):
            return ObjectId(value)
        return value
    
    @validator("parent_id", pre=False)
    def parent_id_convert_object_id(cls, value):
        if value and isinstance(value, str):
            return ObjectId(value)
        return value

    @root_validator
    def number_validator(cls, values):
        values["created_at"] = datetime.now().strftime("%Y-%m-%d %X")
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        return data