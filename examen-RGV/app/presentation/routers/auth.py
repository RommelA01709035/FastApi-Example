from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.presentation.controllers import auth as controller

router = APIRouter(tags=["auth"], include_in_schema=False)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next: str | None = None):
    return controller.login_page(request, next)


@router.post("/login")
def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str | None = Form(None),
    db: Session = Depends(get_db),
):
    return controller.login_form(request, db, email, password, next)


@router.post("/logout")
def logout():
    return controller.logout()
