from decimal import Decimal

from sqlalchemy import Numeric, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.infrastructure.database import Base


class BankAccount(Base):
    __tablename__ = "cuentas_bancarias"

    id: Mapped[int] = mapped_column(primary_key=True)
    bank_name: Mapped[str] = mapped_column("nombre_banco", String(80))
    account_number: Mapped[str] = mapped_column("numero_cuenta", String(30), unique=True)
    balance: Mapped[Decimal] = mapped_column("saldo", Numeric(14, 2), default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column("moneda", String(3), default="MXN")

    @classmethod
    def get_by_number(cls, db: Session, account_number: str) -> "BankAccount | None":
        return db.scalar(select(cls).where(cls.account_number == account_number))

    @classmethod
    def get_for_update(cls, db: Session, id: int) -> "BankAccount | None":
        return db.scalar(select(cls).where(cls.id == id).with_for_update())
