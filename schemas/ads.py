from pydantic import BaseModel, validator
from bson import ObjectId

from functions.function import string_to_ordering
class AdsQueryParams(BaseModel):
    keyword: str=None
    page: int= 1
    page_size: int = 10
    ordering :str = ""
        
    @validator("ordering", pre=False)
    def split_ordering_string(cls, value):
        try:
            if value and isinstance(value, str):
                value = string_to_ordering(value)
                return value
            return {"created_at":1}
        except:
            return {"created_at":1}