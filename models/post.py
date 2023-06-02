from pydantic import BaseModel,root_validator
from datetime import datetime
from models.category import Category

class Post(BaseModel):
    name: str =""
    categories: list(str)= []

    deleted_flag :bool = False
    created_at: str = datetime.now().strftime("%Y-%m-%d %X")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %X")

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now().strftime("%Y-%m-%d %X")
        return values