import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.accounts.models import BankAccount
from app.domain.errors import BusinessRuleError, NotFoundError
from app.domain.expenses.models import Expense, ExpenseEvent, ExpenseRecord, ExpenseStatus
from app.domain.payments.models import OPEN_STATUSES, Payment, PaymentEvent, PaymentRecord, PaymentStatus
from app.infrastructure.database import now


def list_payments(
    db: Session, limit: int, offset: int, status: PaymentStatus | None = None
) -> tuple[list[Payment], int]:
    filters = {"status": status} if status else {}
    return Payment.list(db, limit, offset, **filters)


def list_payments_by_expense(db: Session, expense_id: int) -> list[Payment]:
    return Payment.all(db, expense_id=expense_id)


def get_payment(db: Session, payment_id: int) -> Payment:
    payment = Payment.get(db, payment_id)
    if not payment:
        raise NotFoundError(f"Pago {payment_id} no encontrado")
    return payment


def generate_payment(
    db: Session,
    expense_id: int,
    bank_account_id: int,
    user_id: int,
    amount: Decimal | None = None,
) -> Payment:
    expense = Expense.get(db, expense_id)
    if not expense:
        raise NotFoundError(f"Gasto {expense_id} no encontrado")
    account = BankAccount.get(db, bank_account_id)
    if not account:
        raise NotFoundError(f"Cuenta {bank_account_id} no encontrada")


    # Aqui las condcionales a evaluar
    if expense.status == ExpenseStatus.CANCELLED:
        raise BusinessRuleError("No se puede pagar un gasto cancelado")
    if expense.status == ExpenseStatus.PAID:
        raise BusinessRuleError("El gasto ya está pagado por completo")
    if expense.status != ExpenseStatus.APPROVED:
        raise BusinessRuleError("El gasto debe estar aprobado antes de pagar")

    if Payment.exists_open_for_expense(db, expense.id):
        raise BusinessRuleError("Ya existe un pago pendiente o aprobado para este gasto")

    amount = expense.pending_balance if amount is None else amount
    if amount <= 0:
        raise BusinessRuleError("El monto del pago debe ser mayor a cero")
    if amount > expense.pending_balance:
        raise BusinessRuleError(
            f"El pago ({amount}) excede el saldo pendiente del gasto ({expense.pending_balance})"
        )
    if amount > account.balance:
        raise BusinessRuleError(f"Saldo insuficiente en la cuenta: saldo {account.balance}, pago {amount}")

    payment = Payment(
        expense_id=expense.id,
        bank_account_id=account.id,
        operation_code=f"P-{uuid.uuid4().hex[:10].upper()}",
        amount=amount,
        status=PaymentStatus.PENDING,
        created_by=user_id,
    ).save(db)
    PaymentRecord.create(db, payment.id, PaymentEvent.CREATED, user_id)
    return payment


def approve_payment(db: Session, payment_id: int, user_id: int) -> Payment:
    payment = get_payment(db, payment_id)
    if payment.status != PaymentStatus.PENDING:
        raise BusinessRuleError(f"Solo se aprueban pagos pendientes (estado: {payment.status.value})")

    payment.status = PaymentStatus.APPROVED
    payment.approved_by = user_id
    payment.save(db)
    PaymentRecord.create(db, payment.id, PaymentEvent.APPROVED, user_id)
    return payment


def cancel_payment(db: Session, payment_id: int, user_id: int, reason: str = "") -> Payment:
    payment = get_payment(db, payment_id)
    if payment.status not in OPEN_STATUSES:
        raise BusinessRuleError(f"No se puede cancelar un pago {payment.status.value}")

    payment.status = PaymentStatus.CANCELLED
    payment.save(db)
    PaymentRecord.create(db, payment.id, PaymentEvent.CANCELLED, user_id, reason)
    return payment


def execute_payment(db: Session, payment_id: int, user_id: int) -> Payment:
    payment = get_payment(db, payment_id)
    if payment.status != PaymentStatus.APPROVED:
        raise BusinessRuleError("El pago debe estar aprobado antes de efectuarse")

    expense = Expense.get(db, payment.expense_id)
    if expense.status != ExpenseStatus.APPROVED:
        raise BusinessRuleError(f"El gasto no está aprobado (estado: {expense.status.value})")
    if payment.amount > expense.pending_balance:
        raise BusinessRuleError("El pago excede el saldo pendiente del gasto")

    account = BankAccount.get_for_update(db, payment.bank_account_id)
    if payment.amount > account.balance:
        raise BusinessRuleError(f"Saldo insuficiente: saldo {account.balance}, pago {payment.amount}")

    account.balance -= payment.amount
    account.save(db)

    expense.pending_balance -= payment.amount
    if expense.pending_balance == 0:
        expense.status = ExpenseStatus.PAID
    expense.save(db)
    ExpenseRecord.create(
        db, expense.id, ExpenseEvent.PAID, user_id,
        f"Pago {payment.operation_code} por {payment.amount}",
    )

    payment.status = PaymentStatus.EXECUTED
    payment.executed_at = now()
    payment.save(db)
    PaymentRecord.create(db, payment.id, PaymentEvent.EXECUTED, user_id)
    return payment
