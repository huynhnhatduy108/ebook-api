from pydantic import BaseModel, validator
from bson import ObjectId

def serializeDict(a) -> dict:
    return {**{i:str(a[i]) for i in a if i=='_id'},**{i:a[i] for i in a if i!='_id'}}

def serializeList(entity) -> list:
    return [serializeDict(a) for a in entity]

class PostQueryParams(BaseModel):
    keyword: str=None
    tags: str=None
    categories: str=None
    page: int= 1
    page_size: int = 10

    @validator("tags", pre=False)
    def split_tags_string(cls, value):
        try:
            if isinstance(value, str):
                value = value.split(",")
                return value
            return value
        except:
            return value
        
    @validator("categories", pre=False)
    def split_categories_string(cls, value):
        try:
            if isinstance(value, str):
                value = [ObjectId(cate) for cate in value.split(",")]
                return value
            return value
        except:
            return value
    