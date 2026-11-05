from collections import Counter, defaultdict
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.accounts.models import BankAccount
from app.domain.expenses.models import Expense, ExpenseStatus
from app.domain.payments.models import Payment, PaymentStatus


def get_summary(db: Session) -> dict:
    expenses = Expense.all(db)
    payments = Payment.all(db)
    accounts = BankAccount.all(db)

    active = [expense for expense in expenses if expense.status != ExpenseStatus.CANCELLED]
    executed = [payment for payment in payments if payment.status == PaymentStatus.EXECUTED]

    expenses_by_status = Counter(expense.status.value for expense in expenses)
    payments_by_status = Counter(payment.status.value for payment in payments)

    paid_by_month: dict[str, Decimal] = defaultdict(Decimal)
    for payment in executed:
        paid_by_month[payment.executed_at.strftime("%Y-%m")] += payment.amount

    return {
        "total_expenses": sum((expense.total_amount for expense in active), Decimal("0")),
        "pending_balance": sum((expense.pending_balance for expense in active), Decimal("0")),
        "total_paid": sum((payment.amount for payment in executed), Decimal("0")),
        "bank_balance": sum((account.balance for account in accounts), Decimal("0")),
        "expenses_by_status": {expense.value: expenses_by_status[expense.value] for expense in ExpenseStatus},
        "payments_by_status": {payment.value: payments_by_status[payment.value] for payment in PaymentStatus},
        "balance_by_account": [
            {"account": f"{account.bank_name} {account.account_number}", "balance": account.balance} for account in accounts
        ],
        "paid_by_month": [{"month": month, "amount": amount} for month, amount in sorted(paid_by_month.items())],
        "latest_expenses": expenses[:5],
        "latest_payments": payments[:5],
    }
