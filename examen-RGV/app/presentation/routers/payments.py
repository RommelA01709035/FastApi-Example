from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.domain.payments.models import PaymentStatus
from app.domain.users.models import User
from app.infrastructure.database import get_db
from app.infrastructure.middlewares.auth import get_current_user
from app.presentation.controllers import payments as controller
from app.presentation.schemas.common import CancelIn
from app.presentation.schemas.payments import PaymentList, PaymentOut

router = APIRouter(tags=["payments"])


@router.get("/api/payments", response_model=PaymentList)
def list_payments(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: PaymentStatus | None = None,
    db: Session = Depends(get_db),
):
    return controller.list_payments(db, limit, offset, status)


@router.get("/api/payments/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return controller.get_payment(db, payment_id)


@router.post("/api/payments/{payment_id}/approve", response_model=PaymentOut)
def approve_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.approve_payment(db, payment_id, user.id)


@router.post("/api/payments/{payment_id}/cancel", response_model=PaymentOut)
def cancel_payment(
    payment_id: int,
    body: CancelIn | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.cancel_payment(db, payment_id, user.id, body.reason if body else "")


@router.post("/api/payments/{payment_id}/execute", response_model=PaymentOut)
def execute_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.execute_payment(db, payment_id, user.id)


@router.get("/payments", response_class=HTMLResponse, include_in_schema=False)
def payments_page(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: PaymentStatus | None = None,
    db: Session = Depends(get_db),
):
    return controller.payments_page(request, db, limit, offset, status)


@router.get("/payments/{payment_id}", response_class=HTMLResponse, include_in_schema=False)
def payment_detail_page(request: Request, payment_id: int, db: Session = Depends(get_db)):
    return controller.payment_detail_page(request, db, payment_id)


@router.post("/payments/{payment_id}/approve", include_in_schema=False)
def approve_payment_form(
    payment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.approve_payment_form(db, payment_id, user.id)


@router.post("/payments/{payment_id}/cancel", include_in_schema=False)
def cancel_payment_form(
    payment_id: int,
    reason: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.cancel_payment_form(db, payment_id, user.id, reason)


@router.post("/payments/{payment_id}/execute", include_in_schema=False)
def execute_payment_form(
    payment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return controller.execute_payment_form(db, payment_id, user.id)
