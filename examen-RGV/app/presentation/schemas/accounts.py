from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    bank_name: str = Field(min_length=1, max_length=80)
    account_number: str = Field(min_length=1, max_length=30)
    balance: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    currency: str = Field(default="MXN", min_length=3, max_length=3)


class DepositIn(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bank_name: str
    account_number: str
    balance: Decimal
    currency: str


class AccountList(BaseModel):
    accounts: list[AccountOut]
    total: int
    limit: int
    offset: int
