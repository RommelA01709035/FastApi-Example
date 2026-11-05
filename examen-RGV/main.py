from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI  
from fastapi.exceptions import RequestValidationError  
from starlette.exceptions import HTTPException as StarletteHTTPException  

from app.domain.errors import DomainError  
from app.infrastructure.middlewares.auth import auth_middleware  
from app.presentation.controllers import errors  
from app.presentation.routers import accounts, auth, dashboard, expenses, payments, users  

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
