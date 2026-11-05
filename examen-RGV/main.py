from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402
from starlette.exceptions import HTTPException as StarletteHTTPException  # noqa: E402

from app.domain.errors import DomainError  # noqa: E402
from app.infrastructure.middlewares.auth import auth_middleware  # noqa: E402
from app.presentation.controllers import errors  # noqa: E402
from app.presentation.routers import accounts, auth, dashboard, expenses, payments, users  # noqa: E402

app = FastAPI(title="Control de gastos y pagos")
app.middleware("http")(auth_middleware)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(expenses.router)
app.include_router(payments.router)
app.include_router(accounts.router)
app.include_router(users.router)

app.add_exception_handler(StarletteHTTPException, errors.http_error)
app.add_exception_handler(RequestValidationError, errors.validation_error)
app.add_exception_handler(DomainError, errors.domain_error)
