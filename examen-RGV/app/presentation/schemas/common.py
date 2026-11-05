from pydantic import BaseModel, Field


class CancelIn(BaseModel):
    reason: str = Field(default="", max_length=500)
