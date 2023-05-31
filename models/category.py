from pydantic import BaseModel,root_validator
from datetime import datetime

from models.ebook import Ebook
from models.post import Post

class Category(BaseModel):
    name :str = ""
    name_en:str = ""
    slug :str = ""
    thumbnail :str = ""
    description :str = ""
    ebook:list[Ebook] = []
    post: list[Post]=[]
    deleted_flag :bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now()
        return values
