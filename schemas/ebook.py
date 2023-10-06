from pydantic import BaseModel, validator
from bson import ObjectId

from functions.function import string_to_ordering

def serializeDict(a) -> dict:
    return {**{i:str(a[i]) for i in a if i=='_id'},**{i:a[i] for i in a if i!='_id'}}

def serializeList(entity) -> list:
    return [serializeDict(a) for a in entity]

class EbookQueryParams(BaseModel):
    keyword: str=None
    tags: str=None
    categories: str=None
    language:str =None
    page: int= 1
    page_size: int = 10
    ordering :str = ""

    @validator("tags", pre=False)
    def split_tags_string(cls, value):
        try:
            if value and isinstance(value, str):
                value = value.split(",")
                return value
            return value
        except:
            return value
        
    @validator("categories", pre=False)
    def split_categories_string(cls, value):
        try:
            if value and isinstance(value, str):
                value = [cate for cate in value.split(",")]
                return value
            return value
        except:
            return value
        
    @validator("ordering", pre=False)
    def split_ordering_string(cls, value):
        try:
            if value and isinstance(value, str):
                value = string_to_ordering(value)
                return value
            return {"updated_at":1}
        except:
            return {"updated_at":1}
