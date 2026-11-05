from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.domain.users import usecases
from app.infrastructure.security import SESSION_COOKIE, SESSION_MAX_AGE, create_session_token
from app.presentation.web import render, safe_next


def login_page(request: Request, next_url: str | None):
    return render(request, "auth/login.html", next=safe_next(next_url))


def login_form(request: Request, db: Session, email: str, password: str, next_url: str | None):
    user = usecases.authenticate(db, email.strip(), password)
    if not user:
        return render(
            request,
            "auth/login.html",
            status_code=401,
            next=safe_next(next_url),
            email=email,
            error="Correo o contraseña incorrectos",
        )

    response = RedirectResponse(safe_next(next_url), status_code=303)
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(user.id),
        max_age=SESSION_MAX_AGE,
        httponly=True,  
        samesite="lax", 
        secure=request.url.scheme == "https",
    )
    return response


def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response
