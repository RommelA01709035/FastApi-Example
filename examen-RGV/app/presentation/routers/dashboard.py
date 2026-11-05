from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.presentation.controllers import dashboard as controller
from app.presentation.schemas.dashboard import DashboardOut

router = APIRouter(tags=["dashboard"])


@router.get("/api/dashboard", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    return controller.get_dashboard(db)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    return controller.dashboard_page(request, db)
