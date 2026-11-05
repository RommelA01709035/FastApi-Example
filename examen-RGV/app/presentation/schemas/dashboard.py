from decimal import Decimal

from pydantic import BaseModel

from app.presentation.schemas.expenses import ExpenseOut
from app.presentation.schemas.payments import PaymentOut


class AccountBalance(BaseModel):
    account: str
    balance: Decimal


class MonthTotal(BaseModel):
    month: str
    amount: Decimal


class DashboardOut(BaseModel):
    total_expenses: Decimal
    pending_balance: Decimal
    total_paid: Decimal
    bank_balance: Decimal
    expenses_by_status: dict[str, int]
    payments_by_status: dict[str, int]
    balance_by_account: list[AccountBalance]
    paid_by_month: list[MonthTotal]
    latest_expenses: list[ExpenseOut]
    latest_payments: list[PaymentOut]
