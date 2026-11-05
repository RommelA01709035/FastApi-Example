from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    role_id: int
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    second_last_name: str | None = Field(default=None, max_length=80)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role_id: int
    email: str
    first_name: str
    last_name: str
    second_last_name: str | None


class UserList(BaseModel):
    users: list[UserOut]
    total: int
    limit: int
    offset: int
