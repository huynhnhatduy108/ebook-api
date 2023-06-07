from pydantic import BaseModel, validator
from functions.function import string_to_ordering

def userEntity(item) -> dict:
    return {
        "id":str(item["_id"]),
        "name":item["name"],
        "email":item["email"],
        "password":item["password"]
    }

def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]

#Best way
def serializeDict(a) -> dict:
    return {**{i:str(a[i]) for i in a if i=='_id'},**{i:a[i] for i in a if i!='_id'}}

def serializeList(entity) -> list:
    return [serializeDict(a) for a in entity]

class UserQueryParams(BaseModel):
    keyword: str=None
    role: int=None
    provider: str = ""
    page: int= 1
    page_size: int = 10
    ordering :str = ""

    @validator("ordering", pre=False)
    def split_ordering_string(cls, value):
        try:
            if value and isinstance(value, str):
                value = string_to_ordering(value)
                return value
            return {"updated_at":1}
        except:
            return {"updated_at":1}


