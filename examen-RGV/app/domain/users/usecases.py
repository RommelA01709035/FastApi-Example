from sqlalchemy.orm import Session

from app.domain.errors import BusinessRuleError, NotFoundError
from app.domain.users.models import Role, User
from app.infrastructure.security import hash_password, verify_password


def list_users(db: Session, limit: int, offset: int) -> tuple[list[User], int]:
    return User.list(db, limit, offset)


def get_user(db: Session, user_id: int) -> User:
    user = User.get(db, user_id)
    if not user:
        raise NotFoundError(f"Usuario {user_id} no encontrado")
    return user


def create_user(
    db: Session,
    role_id: int,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    second_last_name: str | None = None,
) -> User:
    if not Role.get(db, role_id):
        raise NotFoundError(f"Rol {role_id} no encontrado")
    if User.get_by_email(db, email):
        raise BusinessRuleError(f"El correo '{email}' ya está registrado")

    user = User(
        role_id=role_id,
        email=email,
        password=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        second_last_name=second_last_name,
    )
    return user.save(db)


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = User.get_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return None
    return user
