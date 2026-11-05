from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.accounts.models import BankAccount
from app.domain.errors import BusinessRuleError, NotFoundError


def list_accounts(db: Session, limit: int, offset: int) -> tuple[list[BankAccount], int]:
    return BankAccount.list(db, limit, offset)


def all_accounts(db: Session) -> list[BankAccount]:
    return BankAccount.all(db)


def get_account(db: Session, account_id: int) -> BankAccount:
    account = BankAccount.get(db, account_id)
    if not account:
        raise NotFoundError(f"Cuenta {account_id} no encontrada")
    return account


def create_account(
    db: Session,
    bank_name: str,
    account_number: str,
    balance: Decimal | None = Decimal("0.00"),
    currency: str = "MXN",
) -> BankAccount:
    balance = Decimal("0.00") if balance is None else balance
    if not bank_name or not account_number:
        raise BusinessRuleError("Banco y número de cuenta son obligatorios")
    if BankAccount.get_by_number(db, account_number):
        raise BusinessRuleError(f"Ya existe la cuenta {account_number}")
    if balance < 0:
        raise BusinessRuleError("El saldo inicial no puede ser negativo")

    return BankAccount(
        bank_name=bank_name,
        account_number=account_number,
        balance=balance,
        currency=(currency or "MXN").upper(),
    ).save(db)


def deposit(db: Session, account_id: int, amount: Decimal | None) -> BankAccount:
    if amount is None or amount <= 0:
        raise BusinessRuleError("El depósito debe ser mayor a cero")
    account = BankAccount.get_for_update(db, account_id)
    if not account:
        raise NotFoundError(f"Cuenta {account_id} no encontrada")
    account.balance += amount
    return account.save(db)
