import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.errors import BusinessRuleError, NotFoundError
from app.domain.expenses.models import Expense, ExpenseEvent, ExpenseRecord, ExpenseStatus
from app.domain.payments.models import OPEN_STATUSES, Payment, PaymentEvent, PaymentRecord, PaymentStatus
from app.infrastructure.database import now


def list_expenses(
    db: Session, limit: int, offset: int, status: ExpenseStatus | None = None
) -> tuple[list[Expense], int]:
    filters = {"status": status} if status else {}
    return Expense.list(db, limit, offset, **filters)


def get_expense(db: Session, expense_id: int) -> Expense:
    expense = Expense.get(db, expense_id)
    if not expense:
        raise NotFoundError(f"Gasto {expense_id} no encontrado")
    return expense


def create_expense(
    db: Session,
    concept: str,
    total_amount: Decimal | None,
    created_by: int,
    description: str | None = None,
) -> Expense:
    if not concept or not concept.strip():
        raise BusinessRuleError("El concepto es obligatorio")
    if total_amount is None or total_amount <= 0:
        raise BusinessRuleError("El monto del gasto debe ser mayor a cero")

    expense = Expense(
        reference_code=f"G-{uuid.uuid4().hex[:8].upper()}",
        concept=concept.strip(),
        description=description,
        total_amount=total_amount,
        pending_balance=total_amount,
        status=ExpenseStatus.PENDING,
        created_by=created_by,
    ).save(db)
    ExpenseRecord.create(db, expense.id, ExpenseEvent.CREATED, created_by)
    return expense


def approve_expense(db: Session, expense_id: int, user_id: int) -> Expense:
    expense = get_expense(db, expense_id)
    if expense.status == ExpenseStatus.CANCELLED:
        raise BusinessRuleError("Un gasto cancelado no se puede reactivar")
    if expense.status != ExpenseStatus.PENDING:
        raise BusinessRuleError(
            f"Solo se aprueban gastos pendientes (estado actual: {expense.status.value})"
        )

    expense.status = ExpenseStatus.APPROVED
    expense.approved_by = user_id
    expense.approved_at = now()
    expense.save(db)
    ExpenseRecord.create(db, expense.id, ExpenseEvent.APPROVED, user_id)
    return expense


def cancel_expense(db: Session, expense_id: int, user_id: int, reason: str = "") -> Expense:
    expense = get_expense(db, expense_id)
    if expense.status == ExpenseStatus.CANCELLED:
        raise BusinessRuleError("El gasto ya está cancelado")
    if expense.status == ExpenseStatus.PAID:
        raise BusinessRuleError("No se puede cancelar un gasto pagado")
    if expense.pending_balance < expense.total_amount:
        raise BusinessRuleError("No se puede cancelar un gasto con pagos efectuados")

    for payment in Payment.all(db, expense_id=expense.id):
        if payment.status in OPEN_STATUSES:
            payment.status = PaymentStatus.CANCELLED
            payment.save(db)
            PaymentRecord.create(db, payment.id, PaymentEvent.CANCELLED, user_id, "Gasto cancelado")

    expense.status = ExpenseStatus.CANCELLED
    expense.save(db)
    ExpenseRecord.create(db, expense.id, ExpenseEvent.CANCELLED, user_id, reason)
    return expense
