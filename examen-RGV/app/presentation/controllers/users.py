from fastapi import Request
from sqlalchemy.orm import Session

from app.domain.users import usecases
from app.presentation.schemas.users import UserCreate, UserList, UserOut
from app.presentation.web import render


def list_users(db: Session, limit: int, offset: int) -> UserList:
    items, total = usecases.list_users(db, limit, offset)
    return UserList(
        users=[UserOut.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


def get_user(db: Session, user_id: int) -> UserOut:
    return UserOut.model_validate(usecases.get_user(db, user_id))


def create_user(db: Session, body: UserCreate) -> UserOut:
    return UserOut.model_validate(usecases.create_user(db, **body.model_dump()))


def users_page(request: Request, db: Session, limit: int, offset: int):
    return render(request, "users/list.html", page=list_users(db, limit, offset))
