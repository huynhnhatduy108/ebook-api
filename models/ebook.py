from pydantic import BaseModel,root_validator
from datetime import datetime
from functions.function import gen_slug_radom_string
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
    admin: str = None
    tags: list[str] = []
    categories: list[str] =[]
    img_url:str = ""
    pdf_url : str = ""

    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values


class EbookView(BaseModel):
    ebook: str
    view: int 

class EbookDownload(BaseModel):
    ebook: str
    num_download: int 

class EbookRate(BaseModel):
    ebook_id: str
    user : str
    rate: int =0

    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values


class EbookComment(BaseModel):
    ebook: str
    user : str
    parent:str
    content:str

    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values


