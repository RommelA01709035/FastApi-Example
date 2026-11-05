from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.infrastructure.database import Base, now


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String(50), unique=True)

    users: Mapped[list["User"]] = relationship(back_populates="role")

    @classmethod
    def get_by_name(cls, db: Session, name: str) -> "Role | None":
        return db.scalar(select(cls).where(cls.name == name))


class Feature(Base):
    __tablename__ = "funcionalidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String(80))
    route: Mapped[str] = mapped_column("ruta", String(120), unique=True)

    @classmethod
    def get_by_route(cls, db: Session, route: str) -> "Feature | None":
        return db.scalar(select(cls).where(cls.route == route))


class RoleFeature(Base):
    __tablename__ = "rol_funcionalidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column("id_rol", ForeignKey("roles.id"), index=True)
    feature_id: Mapped[int] = mapped_column(
        "id_funcionalidad", ForeignKey("funcionalidades.id"), index=True
    )

    @classmethod
    def exists(cls, db: Session, role_id: int, feature_id: int) -> bool:
        query = select(cls.id).where(cls.role_id == role_id, cls.feature_id == feature_id)
        return db.scalar(query) is not None


class User(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column("id_rol", ForeignKey("roles.id"))
    email: Mapped[str] = mapped_column("correo", String(120), unique=True, index=True)
    password: Mapped[str] = mapped_column("password", String(255))
    first_name: Mapped[str] = mapped_column("nombre", String(80))
    last_name: Mapped[str] = mapped_column("apellido_paterno", String(80))
    second_last_name: Mapped[str | None] = mapped_column("apellido_materno", String(80))

    role: Mapped[Role] = relationship(back_populates="users")

    @classmethod
    def get_by_email(cls, db: Session, email: str) -> "User | None":
        return db.scalar(select(cls).where(cls.email == email))


class FeatureLog(Base):
    __tablename__ = "logger_funcionalidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    feature_id: Mapped[int] = mapped_column(
        "id_funcionalidad", ForeignKey("funcionalidades.id"), index=True
    )
    user_id: Mapped[int] = mapped_column("id_usuario", ForeignKey("usuarios.id"), index=True)
    created_at: Mapped[datetime] = mapped_column("fecha_registro", DateTime(timezone=True), default=now)
