from pydantic import BaseModel,root_validator

class Dashboard(BaseModel):
    total_view : int