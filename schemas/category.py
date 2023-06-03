from pydantic import BaseModel

def serializeDict(a) -> dict:
    return {**{i:str(a[i]) for i in a if i=='_id'},**{i:a[i] for i in a if i!='_id'}}

def serializeList(entity) -> list:
    return [serializeDict(a) for a in entity]

class CategoryQueryParams(BaseModel):
    keyword: str=None
    ebook:str =None
    post: str=None
    page: int= 1
    page_size: int = 10
