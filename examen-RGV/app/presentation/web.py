from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlencode

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.domain.errors import BusinessRuleError, DomainError

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

templates.env.globals["status_labels"] = {
    "PENDING": "Pendiente",
    "APPROVED": "Aprobado",
    "PAID": "Pagado",
    "EXECUTED": "Efectuado",
    "CANCELLED": "Cancelado",
    "CREATED": "Creado",
}
templates.env.globals["status_colors"] = {
    "PENDING": "is-warning",
    "APPROVED": "is-info",
    "PAID": "is-success",
    "EXECUTED": "is-success",
    "CANCELLED": "is-danger",
    "CREATED": "is-light",
}
templates.env.filters["money"] = lambda value: f"${value:,.2f}"
templates.env.filters["datetime"] = lambda value: value.strftime("%d/%m/%Y %H:%M") if value else "—"


def render(request: Request, name: str, status_code: int = 200, **context):
    return templates.TemplateResponse(request, name, context, status_code=status_code)


def safe_next(url: str | None) -> str:
    return url if url and url.startswith("/") and not url.startswith("//") else "/"


def redirect(url: str, ok: str | None = None, error: str | None = None) -> RedirectResponse:
    params = {key: value for key, value in {"ok": ok, "error": error}.items() if value}
    return RedirectResponse(f"{url}?{urlencode(params)}" if params else url, status_code=303)


def run_action(db: Session, action: Callable[[], object], back: str, ok_message: str):
    try:
        action()
    except DomainError as exc:
        db.rollback()
        return redirect(back, error=exc.message)
    return redirect(back, ok=ok_message)


def parse_money(text: str | None) -> Decimal | None:
    if not text or not text.strip():
        return None
    try:
        return Decimal(text.strip())
    except InvalidOperation as exc:
        raise BusinessRuleError(f"Monto inválido: {text}") from exc
