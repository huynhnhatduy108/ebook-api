from pydantic import BaseModel, validator
from bson import ObjectId
class CategoryQueryParams(BaseModel):
    keyword: str=None
    ebooks:str =None
    posts: str=None
    page: int= 1
    page_size: int = 10

    @validator("ebooks", pre=False)
    def split_ebooks_string(cls, value):
        try:
            if value and isinstance(value, str):
                value = value.split(",")
                return value
            return value
        except:
            return value
        
    @validator("posts", pre=False)
    def split_posts_string(cls, value):
        try:
            if value and isinstance(value, str):
                value = [ObjectId(cate) for cate in value.split(",")]
                return value
            return value
        except:
            return value
