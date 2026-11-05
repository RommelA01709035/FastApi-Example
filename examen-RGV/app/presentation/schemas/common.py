from pydantic import BaseModel, BeforeValidator, Field

EmptyAsNone = BeforeValidator(lambda value: None if value == "" else value)


class CancelIn(BaseModel):
    reason: str = Field(default="", max_length=500)
