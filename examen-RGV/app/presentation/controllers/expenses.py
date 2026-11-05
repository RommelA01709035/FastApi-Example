from fastapi import Request
from sqlalchemy.orm import Session

from app.domain.accounts import usecases as accounts
from app.domain.expenses import usecases
from app.domain.expenses.models import ExpenseStatus
from app.domain.payments import usecases as payments
from app.presentation.schemas.expenses import ExpenseCreate, ExpenseList, ExpenseOut
from app.presentation.schemas.payments import PaymentCreate, PaymentOut
from app.presentation.web import parse_money, render, run_action


def list_expenses(db: Session, limit: int, offset: int, status: ExpenseStatus | None) -> ExpenseList:
    items, total = usecases.list_expenses(db, limit, offset, status)
    return ExpenseList(
        expenses=[ExpenseOut.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


def get_expense(db: Session, expense_id: int) -> ExpenseOut:
    return ExpenseOut.model_validate(usecases.get_expense(db, expense_id))


def create_expense(db: Session, body: ExpenseCreate, user_id: int) -> ExpenseOut:
    expense = usecases.create_expense(db, **body.model_dump(), created_by=user_id)
    return ExpenseOut.model_validate(expense)


def approve_expense(db: Session, expense_id: int, user_id: int) -> ExpenseOut:
    return ExpenseOut.model_validate(usecases.approve_expense(db, expense_id, user_id))


def cancel_expense(db: Session, expense_id: int, user_id: int, reason: str) -> ExpenseOut:
    return ExpenseOut.model_validate(usecases.cancel_expense(db, expense_id, user_id, reason))


def generate_payment(db: Session, expense_id: int, body: PaymentCreate, user_id: int) -> PaymentOut:
    payment = payments.generate_payment(db, expense_id, body.bank_account_id, user_id, body.amount)
    return PaymentOut.model_validate(payment)


def expenses_page(request: Request, db: Session, limit: int, offset: int, status: ExpenseStatus | None):
    return render(
        request,
        "expenses/list.html",
        page=list_expenses(db, limit, offset, status),
        status=status.value if status else "",
        statuses=list(ExpenseStatus),
    )


def expense_detail_page(request: Request, db: Session, expense_id: int):
    return render(
        request,
        "expenses/detail.html",
        expense=usecases.get_expense(db, expense_id),
        payments=payments.list_payments_by_expense(db, expense_id),
        accounts=accounts.all_accounts(db),
    )


def create_expense_form(db: Session, concept: str, total_amount: str, description: str, user_id: int):
    return run_action(
        db,
        lambda: usecases.create_expense(db, concept, parse_money(total_amount), user_id, description or None),
        "/expenses",
        "Gasto creado",
    )


def approve_expense_form(db: Session, expense_id: int, user_id: int):
    return run_action(
        db,
        lambda: usecases.approve_expense(db, expense_id, user_id),
        f"/expenses/{expense_id}",
        "Gasto aprobado",
    )


def cancel_expense_form(db: Session, expense_id: int, user_id: int, reason: str):
    return run_action(
        db,
        lambda: usecases.cancel_expense(db, expense_id, user_id, reason),
        f"/expenses/{expense_id}",
        "Gasto cancelado",
    )


def generate_payment_form(db: Session, expense_id: int, bank_account_id: int, amount: str, user_id: int):
    return run_action(
        db,
        lambda: payments.generate_payment(db, expense_id, bank_account_id, user_id, parse_money(amount)),
        f"/expenses/{expense_id}",
        "Pago generado (pendiente de aprobación)",
    )
