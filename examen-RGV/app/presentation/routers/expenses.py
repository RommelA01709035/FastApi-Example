from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.domain.expenses.models import ExpenseStatus
from app.domain.users.models import User
from app.infrastructure.database import get_db
from app.infrastructure.middlewares.auth import get_current_user
from app.presentation.controllers import expenses as controller
from app.presentation.schemas.common import CancelIn, EmptyAsNone
from app.presentation.schemas.expenses import ExpenseCreate, ExpenseList, ExpenseOut
from app.presentation.schemas.payments import PaymentCreate, PaymentOut

router = APIRouter(tags=["expenses"])


@router.get("/api/expenses", response_model=ExpenseList)
def list_expenses(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Annotated[ExpenseStatus | None, EmptyAsNone] = None,
    db: Session = Depends(get_db),
):
    return controller.list_expenses(db, limit, offset, status)


@router.get("/api/expenses/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    return controller.get_expense(db, expense_id)


@router.post("/api/expenses", response_model=ExpenseOut, status_code=201)
def create_expense(
    body: ExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.create_expense(db, body, user.id)


@router.post("/api/expenses/{expense_id}/approve", response_model=ExpenseOut)
def approve_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.approve_expense(db, expense_id, user.id)


@router.post("/api/expenses/{expense_id}/cancel", response_model=ExpenseOut)
def cancel_expense(
    expense_id: int,
    body: CancelIn | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.cancel_expense(db, expense_id, user.id, body.reason if body else "")


@router.post("/api/expenses/{expense_id}/generate-payment", response_model=PaymentOut, status_code=201)
def generate_payment(
    expense_id: int,
    body: PaymentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.generate_payment(db, expense_id, body, user.id)


@router.get("/expenses", response_class=HTMLResponse, include_in_schema=False)
def expenses_page(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Annotated[ExpenseStatus | None, EmptyAsNone] = None,
    db: Session = Depends(get_db),
):
    return controller.expenses_page(request, db, limit, offset, status)


@router.get("/expenses/{expense_id}", response_class=HTMLResponse, include_in_schema=False)
def expense_detail_page(request: Request, expense_id: int, db: Session = Depends(get_db)):
    return controller.expense_detail_page(request, db, expense_id)


@router.post("/expenses", include_in_schema=False)
def create_expense_form(
    concept: str = Form(...),
    total_amount: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.create_expense_form(db, concept, total_amount, description, user.id)


@router.post("/expenses/{expense_id}/approve", include_in_schema=False)
def approve_expense_form(
    expense_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.approve_expense_form(db, expense_id, user.id)


@router.post("/expenses/{expense_id}/cancel", include_in_schema=False)
def cancel_expense_form(
    expense_id: int,
    reason: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.cancel_expense_form(db, expense_id, user.id, reason)


@router.post("/expenses/{expense_id}/generate-payment", include_in_schema=False)
def generate_payment_form(
    expense_id: int,
    bank_account_id: int = Form(...),
    amount: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.generate_payment_form(db, expense_id, bank_account_id, amount, user.id)
