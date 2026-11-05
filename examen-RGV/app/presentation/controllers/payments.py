from fastapi import Request
from sqlalchemy.orm import Session

from app.domain.accounts import usecases as accounts
from app.domain.expenses import usecases as expenses
from app.domain.payments import usecases
from app.domain.payments.models import PaymentStatus
from app.presentation.schemas.payments import PaymentList, PaymentOut
from app.presentation.web import render, run_action


def list_payments(db: Session, limit: int, offset: int, status: PaymentStatus | None) -> PaymentList:
    items, total = usecases.list_payments(db, limit, offset, status)
    return PaymentList(
        payments=[PaymentOut.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


def get_payment(db: Session, payment_id: int) -> PaymentOut:
    return PaymentOut.model_validate(usecases.get_payment(db, payment_id))


def approve_payment(db: Session, payment_id: int, user_id: int) -> PaymentOut:
    return PaymentOut.model_validate(usecases.approve_payment(db, payment_id, user_id))


def cancel_payment(db: Session, payment_id: int, user_id: int, reason: str) -> PaymentOut:
    return PaymentOut.model_validate(usecases.cancel_payment(db, payment_id, user_id, reason))


def execute_payment(db: Session, payment_id: int, user_id: int) -> PaymentOut:
    return PaymentOut.model_validate(usecases.execute_payment(db, payment_id, user_id))


def payments_page(request: Request, db: Session, limit: int, offset: int, status: PaymentStatus | None):
    return render(
        request,
        "payments/list.html",
        page=list_payments(db, limit, offset, status),
        status=status.value if status else "",
        statuses=list(PaymentStatus),
    )


def payment_detail_page(request: Request, db: Session, payment_id: int):
    payment = usecases.get_payment(db, payment_id)
    return render(
        request,
        "payments/detail.html",
        payment=payment,
        expense=expenses.get_expense(db, payment.expense_id),
        account=accounts.get_account(db, payment.bank_account_id),
    )


def approve_payment_form(db: Session, payment_id: int, user_id: int):
    return run_action(
        db,
        lambda: usecases.approve_payment(db, payment_id, user_id),
        f"/payments/{payment_id}",
        "Pago aprobado",
    )


def cancel_payment_form(db: Session, payment_id: int, user_id: int, reason: str):
    return run_action(
        db,
        lambda: usecases.cancel_payment(db, payment_id, user_id, reason),
        f"/payments/{payment_id}",
        "Pago cancelado",
    )


def execute_payment_form(db: Session, payment_id: int, user_id: int):
    return run_action(
        db,
        lambda: usecases.execute_payment(db, payment_id, user_id),
        f"/payments/{payment_id}",
        "Pago efectuado",
    )
