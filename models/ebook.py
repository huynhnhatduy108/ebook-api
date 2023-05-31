from pydantic import BaseModel,root_validator
from datetime import datetime
from models.category import Category

from models.user import User

class Ebook(BaseModel):
    name:str = ""
    name_en:str = ""
    content:str =""
    content_en:str =""
    intro:str =""
    intro_en:str =""
    auth_name:str =""
    published_at: datetime = None
    admin: User = None
    tags: set[str] = set()
    categories: list[Category] = []
    img_url:str = ""
    pdf_url : str = ""
    deleted_flag :bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now()
        return values