from fastapi import Request
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.errors import DomainError, NotFoundError
from app.infrastructure.middlewares.auth import API_PREFIXES
from app.presentation.web import render


def wants_html(request: Request) -> bool:
    return not request.url.path.startswith(API_PREFIXES)


async def http_error(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404 and wants_html(request):
        return render(request, "errors/404.html", status_code=404)
    return await http_exception_handler(request, exc)


async def validation_error(request: Request, exc: RequestValidationError):
    if request.method == "GET" and wants_html(request):
        return render(request, "errors/404.html", status_code=404)
    return await request_validation_exception_handler(request, exc)


def domain_error(request: Request, exc: DomainError):
    if isinstance(exc, NotFoundError) and wants_html(request):
        return render(request, "errors/404.html", status_code=404, message=exc.message)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
