from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.presentation.controllers import accounts as controller
from app.presentation.schemas.accounts import AccountCreate, AccountList, AccountOut, DepositIn

router = APIRouter(tags=["accounts"])


@router.get("/api/accounts", response_model=AccountList)
def list_accounts(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return controller.list_accounts(db, limit, offset)


@router.get("/api/accounts/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db)):
    return controller.get_account(db, account_id)


@router.post("/api/accounts", response_model=AccountOut, status_code=201)
def create_account(body: AccountCreate, db: Session = Depends(get_db)):
    return controller.create_account(db, body)


@router.post("/api/accounts/{account_id}/deposit", response_model=AccountOut)
def deposit(account_id: int, body: DepositIn, db: Session = Depends(get_db)):
    return controller.deposit(db, account_id, body.amount)


@router.get("/accounts", response_class=HTMLResponse, include_in_schema=False)
def accounts_page(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return controller.accounts_page(request, db, limit, offset)


@router.post("/accounts", include_in_schema=False)
def create_account_form(
    bank_name: str = Form(...),
    account_number: str = Form(...),
    balance: str = Form(""),
    currency: str = Form("MXN"),
    db: Session = Depends(get_db),
):
    return controller.create_account_form(db, bank_name, account_number, balance, currency)


@router.post("/accounts/{account_id}/deposit", include_in_schema=False)
def deposit_form(account_id: int, amount: str = Form(...), db: Session = Depends(get_db)):
    return controller.deposit_form(db, account_id, amount)
