from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.presentation.controllers import users as controller
from app.presentation.schemas.users import UserCreate, UserList, UserOut

router = APIRouter(tags=["users"])


@router.get("/api/users", response_model=UserList)
def list_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return controller.list_users(db, limit, offset)


@router.get("/api/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return controller.get_user(db, user_id)


@router.post("/api/users", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    return controller.create_user(db, body)


@router.get("/users", response_class=HTMLResponse, include_in_schema=False)
def users_page(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return controller.users_page(request, db, limit, offset)
