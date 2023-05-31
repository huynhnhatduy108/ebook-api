from pydantic import BaseModel


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
    page: int= 1
    page_size: int = 10

class UserRegisterDto(BaseModel):
    username :str
    email:str
    full_name:str
    password:str
    role: int=0

class UserLoginDto(BaseModel):
    username :str
    password:str
