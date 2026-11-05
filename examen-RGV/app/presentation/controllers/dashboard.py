from fastapi import Request
from sqlalchemy.orm import Session

from app.domain.dashboard import usecases
from app.presentation.schemas.dashboard import DashboardOut
from app.presentation.web import render


def get_dashboard(db: Session) -> DashboardOut:
    return DashboardOut.model_validate(usecases.get_summary(db), from_attributes=True)


def dashboard_page(request: Request, db: Session):
    summary = get_dashboard(db)
    charts = {
        "expenses_by_status": summary.expenses_by_status,
        "payments_by_status": summary.payments_by_status,
        "balance_by_account": {
            "labels": [item.account for item in summary.balance_by_account],
            "data": [float(item.balance) for item in summary.balance_by_account],
        },
        "paid_by_month": {
            "labels": [item.month for item in summary.paid_by_month],
            "data": [float(item.amount) for item in summary.paid_by_month],
        },
    }
    return render(request, "dashboard.html", summary=summary, charts=charts)
