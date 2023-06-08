from pydantic import BaseModel,root_validator, validator
from datetime import datetime
from functions.function import gen_slug_radom_string
from bson import ObjectId

class Ebook(BaseModel):
    name:str = ""
    name_en:str = ""
    content:str =""
    content_en:str =""
    intro:str =""
    intro_en:str =""
    auth_name:str =""
    published_at: datetime = None
    tags: list[str] = []
    categories: list[str] =[]
    img_url:str = ""
    pdf_url : str = ""
    epub_url:str=""
    mobi_url:str =""
    prc_url:str =""
    azw_url: str =""

    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @validator("categories", pre=False)
    def categories_convert_object_id(cls, value):
        if isinstance(value, list):
            return [ObjectId(v) if isinstance(v, str) else v for v in value]
        return value

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['categories'] = self.categories
        data["deleted_flag"] = False
        return data

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values
    

class EbookView(BaseModel):
    ebook_id: str =""
    view: int 

class EbookDownload(BaseModel):
    ebook_id: str =""
    num_download: int 

class EbookRate(BaseModel):
    ebook_id: str =""
    rate: int = 0

    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @validator("ebook_id", pre=False)
    def ebook_id_convert_object_id(cls, value):
        if value and isinstance(value, str):
            return ObjectId(value)
        return value
    
    @validator("rate", pre=False)
    def rate_range(cls, value):
        if value<=5 and value>0:
            return value
        raise  ValueError("rate must be in range 1 to 5")



    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values
    
    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        return data


