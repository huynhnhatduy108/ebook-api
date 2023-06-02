from pydantic import BaseModel,root_validator
from datetime import datetime

# from models.ebook import Ebook 
# from models.post import Post

class Category(BaseModel):
    name :str = ""
    name_en:str = ""
    slug :str = ""
    thumbnail :str = ""
    description :str = ""
    ebooks:list[str] = []
    post: list[str]=[]
    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values
