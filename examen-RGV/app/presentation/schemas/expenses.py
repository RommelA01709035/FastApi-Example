from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.expenses.models import ExpenseStatus


class ExpenseCreate(BaseModel):
    concept: str = Field(min_length=1, max_length=120)
    description: str | None = None
    total_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_code: str
    concept: str
    description: str | None
    total_amount: Decimal
    pending_balance: Decimal
    status: ExpenseStatus
    created_by: int
    approved_by: int | None
    expense_date: datetime
    approved_at: datetime | None


class ExpenseList(BaseModel):
    expenses: list[ExpenseOut]
    total: int
    limit: int
    offset: int
