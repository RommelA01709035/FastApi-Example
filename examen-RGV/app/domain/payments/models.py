from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, select
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.infrastructure.database import Base, now


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"


class PaymentEvent(str, Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"


OPEN_STATUSES = (PaymentStatus.PENDING, PaymentStatus.APPROVED)


class Payment(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column("id_gasto", ForeignKey("gastos.id"), index=True)
    bank_account_id: Mapped[int] = mapped_column(
        "id_cuenta_bancaria", ForeignKey("cuentas_bancarias.id")
    )
    operation_code: Mapped[str] = mapped_column("codigo_operacion", String(40), unique=True)
    amount: Mapped[Decimal] = mapped_column("monto", Numeric(14, 2))
    status: Mapped[PaymentStatus] = mapped_column(
        "estado", SqlEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True
    )
    created_by: Mapped[int] = mapped_column("creado_por", ForeignKey("usuarios.id"))
    approved_by: Mapped[int | None] = mapped_column("aprobado_por", ForeignKey("usuarios.id"))
    payment_date: Mapped[datetime] = mapped_column("fecha_pago", DateTime(timezone=True), default=now)
    executed_at: Mapped[datetime | None] = mapped_column("fecha_efectuado", DateTime(timezone=True))

    records: Mapped[list["PaymentRecord"]] = relationship(back_populates="payment")

    @classmethod
    def exists_open_for_expense(cls, db: Session, expense_id: int) -> bool:
        query = select(cls.id).where(cls.expense_id == expense_id, cls.status.in_(OPEN_STATUSES))
        return db.scalar(query) is not None


class PaymentRecord(Base):
    __tablename__ = "pago_registros"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column("id_pago", ForeignKey("pagos.id"), index=True)
    event_type: Mapped[PaymentEvent] = mapped_column("tipo_evento", SqlEnum(PaymentEvent))
    performed_by: Mapped[int] = mapped_column("realizado_por", ForeignKey("usuarios.id"))
    detail: Mapped[str | None] = mapped_column("detalle", Text)
    created_at: Mapped[datetime] = mapped_column("fecha_registro", DateTime(timezone=True), default=now)

    payment: Mapped[Payment] = relationship(back_populates="records")

    @classmethod
    def create(cls, db: Session, payment_id: int, event: PaymentEvent, user_id: int, detail: str = ""):
        db.add(cls(payment_id=payment_id, event_type=event, performed_by=user_id, detail=detail))
