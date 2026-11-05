from fastapi import Request
from sqlalchemy.orm import Session

from app.domain.accounts import usecases
from app.presentation.schemas.accounts import AccountCreate, AccountList, AccountOut
from app.presentation.web import parse_money, render, run_action


def list_accounts(db: Session, limit: int, offset: int) -> AccountList:
    items, total = usecases.list_accounts(db, limit, offset)
    return AccountList(
        accounts=[AccountOut.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


def get_account(db: Session, account_id: int) -> AccountOut:
    return AccountOut.model_validate(usecases.get_account(db, account_id))


def create_account(db: Session, body: AccountCreate) -> AccountOut:
    return AccountOut.model_validate(usecases.create_account(db, **body.model_dump()))


def deposit(db: Session, account_id: int, amount) -> AccountOut:
    return AccountOut.model_validate(usecases.deposit(db, account_id, amount))


def accounts_page(request: Request, db: Session, limit: int, offset: int):
    return render(request, "accounts/list.html", page=list_accounts(db, limit, offset))


def create_account_form(db: Session, bank_name: str, account_number: str, balance: str, currency: str):
    return run_action(
        db,
        lambda: usecases.create_account(db, bank_name.strip(), account_number.strip(), parse_money(balance), currency),
        "/accounts",
        "Cuenta creada",
    )


def deposit_form(db: Session, account_id: int, amount: str):
    return run_action(
        db,
        lambda: usecases.deposit(db, account_id, parse_money(amount)),
        "/accounts",
        "Depósito registrado",
    )
