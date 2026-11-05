import base64
import binascii
from urllib.parse import urlencode

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool

from app.domain.users.models import User
from app.domain.users.usecases import authenticate
from app.infrastructure.database import SessionLocal
from app.infrastructure.security import SESSION_COOKIE, read_session_token

PUBLIC_PATHS = {"/login"}
API_PREFIXES = ("/api", "/docs", "/redoc", "/openapi.json")


def user_from_header(authorization: str | None) -> User | None:
    scheme, _, encoded = (authorization or "").partition(" ")
    if scheme.lower() != "basic" or not encoded:
        return None
    try:
        email, sep, password = base64.b64decode(encoded).decode().partition(":")
    except (binascii.Error, UnicodeDecodeError):
        return None
    if not sep:
        return None
    with SessionLocal() as db:
        return authenticate(db, email, password)


def user_from_session(token: str | None) -> User | None:
    user_id = read_session_token(token)
    if user_id is None:
        return None
    with SessionLocal() as db:
        return User.get(db, user_id)


def resolve_user(authorization: str | None, session_token: str | None) -> User | None:
    return user_from_header(authorization) or user_from_session(session_token)


async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    user = await run_in_threadpool(
        resolve_user, request.headers.get("Authorization"), request.cookies.get(SESSION_COOKIE)
    )
    if user:
        request.state.user = user
        return await call_next(request)

    if request.url.path.startswith(API_PREFIXES):
        return JSONResponse(
            status_code=401,
            content={"detail": "Credenciales inválidas o ausentes"},
            headers={"WWW-Authenticate": 'Basic realm="Control de gastos", charset="UTF-8"'},
        )
    return RedirectResponse(f"/login?{urlencode({'next': request.url.path})}", status_code=303)


def get_current_user(request: Request) -> User:
    return request.state.user
