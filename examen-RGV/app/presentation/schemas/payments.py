from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.payments.models import PaymentStatus


class PaymentCreate(BaseModel):
    bank_account_id: int
    amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    expense_id: int
    bank_account_id: int
    operation_code: str
    amount: Decimal
    status: PaymentStatus
    created_by: int
    approved_by: int | None
    payment_date: datetime
    executed_at: datetime | None


class PaymentList(BaseModel):
    payments: list[PaymentOut]
    total: int
    limit: int
    offset: int
