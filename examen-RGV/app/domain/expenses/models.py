from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, select
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.infrastructure.database import Base, now


class ExpenseStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class ExpenseEvent(str, Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Expense(Base):
    __tablename__ = "gastos"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference_code: Mapped[str] = mapped_column("codigo_referencia", String(40), unique=True)
    concept: Mapped[str] = mapped_column("concepto", String(120))
    description: Mapped[str | None] = mapped_column("descripcion", Text)
    total_amount: Mapped[Decimal] = mapped_column("monto_total", Numeric(14, 2))
    pending_balance: Mapped[Decimal] = mapped_column("saldo_pendiente", Numeric(14, 2))
    status: Mapped[ExpenseStatus] = mapped_column(
        "estado", SqlEnum(ExpenseStatus), default=ExpenseStatus.PENDING, index=True
    )
    created_by: Mapped[int] = mapped_column("creado_por", ForeignKey("usuarios.id"))
    approved_by: Mapped[int | None] = mapped_column("aprobado_por", ForeignKey("usuarios.id"))
    expense_date: Mapped[datetime] = mapped_column("fecha_gasto", DateTime(timezone=True), default=now)
    approved_at: Mapped[datetime | None] = mapped_column("fecha_aprobacion", DateTime(timezone=True))

    records: Mapped[list["ExpenseRecord"]] = relationship(back_populates="expense")

    @classmethod
    def get_by_code(cls, db: Session, reference_code: str) -> "Expense | None":
        return db.scalar(select(cls).where(cls.reference_code == reference_code))


class ExpenseRecord(Base):
    __tablename__ = "gasto_registros"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column("id_gasto", ForeignKey("gastos.id"), index=True)
    event_type: Mapped[ExpenseEvent] = mapped_column("tipo_evento", SqlEnum(ExpenseEvent))
    performed_by: Mapped[int] = mapped_column("realizado_por", ForeignKey("usuarios.id"))
    detail: Mapped[str | None] = mapped_column("detalle", Text)
    created_at: Mapped[datetime] = mapped_column("fecha_registro", DateTime(timezone=True), default=now)

    expense: Mapped[Expense] = relationship(back_populates="records")

    @classmethod
    def create(cls, db: Session, expense_id: int, event: ExpenseEvent, user_id: int, detail: str = ""):
        db.add(cls(expense_id=expense_id, event_type=event, performed_by=user_id, detail=detail))
