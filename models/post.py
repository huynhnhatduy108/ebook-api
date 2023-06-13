from pydantic import BaseModel,root_validator, validator
from datetime import datetime
from bson import ObjectId

class Post(BaseModel):
    name: str = ""
    thumbnail: str = ""
    meta_title: str = ""
    sumary: str = ""
    content: str = ""
    categories: list[str] =[]
    tags: list[str] =[]
    ebook_id: str = ""
    is_public:bool= True
    published_at: str = datetime.now().strftime("%Y-%m-%d %X")

    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @validator("categories", pre=False)
    def categories_convert_object_id(cls, value):
        if isinstance(value, list):
            return [ObjectId(v) if isinstance(v, str) else v for v in value]
        return value
    
    @validator("ebook_id", pre=False)
    def ebook_id_convert_object_id(cls, value):
        if value and isinstance(value, str):
            return ObjectId(value)
        return value

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data["views"] = 0
        data['categories'] = self.categories
        data["deleted_flag"] = False
        return data
    

    