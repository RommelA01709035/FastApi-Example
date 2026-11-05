from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
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


API_DOCS = {
    ("/api/dashboard", "get"): (
        "Resumen general",
        "Totales de gastos, saldo pendiente, total pagado y saldo bancario; conteos por estado "
        "de gastos y pagos; saldo por cuenta; pagos por mes; últimos gastos y pagos.",
        {},
    ),
    ("/api/expenses", "get"): (
        "Listar gastos",
        "Gastos paginados con `limit` y `offset`. Filtro opcional por `status`.",
        {},
    ),
    ("/api/expenses/{expense_id}", "get"): (
        "Obtener gasto",
        "Devuelve un gasto por su ID.",
        {404: "Gasto no encontrado"},
    ),
    ("/api/expenses", "post"): (
        "Crear gasto",
        "Registra un gasto en estado PENDING con saldo pendiente igual al monto total.",
        {409: "Concepto vacío o monto menor o igual a cero"},
    ),
    ("/api/expenses/{expense_id}/approve", "post"): (
        "Aprobar gasto",
        "Cambia un gasto PENDING a APPROVED y registra quién lo aprobó.",
        {404: "Gasto no encontrado", 409: "El gasto no está pendiente o está cancelado"},
    ),
    ("/api/expenses/{expense_id}/cancel", "post"): (
        "Cancelar gasto",
        "Cancela el gasto y sus pagos abiertos. Acepta un motivo opcional.",
        {
            404: "Gasto no encontrado",
            409: "El gasto ya está cancelado, está pagado o tiene pagos efectuados",
        },
    ),
    ("/api/expenses/{expense_id}/generate-payment", "post"): (
        "Generar pago",
        "Crea un pago PENDING para un gasto APPROVED desde una cuenta bancaria. "
        "Si no se envía `amount`, se usa el saldo pendiente del gasto.",
        {
            404: "Gasto o cuenta no encontrados",
            409: "Gasto no aprobado, ya existe un pago abierto, monto inválido o saldo insuficiente",
        },
    ),
    ("/api/payments", "get"): (
        "Listar pagos",
        "Pagos paginados con `limit` y `offset`. Filtro opcional por `status`.",
        {},
    ),
    ("/api/payments/{payment_id}", "get"): (
        "Obtener pago",
        "Devuelve un pago por su ID.",
        {404: "Pago no encontrado"},
    ),
    ("/api/payments/{payment_id}/approve", "post"): (
        "Aprobar pago",
        "Cambia un pago PENDING a APPROVED.",
        {404: "Pago no encontrado", 409: "El pago no está pendiente"},
    ),
    ("/api/payments/{payment_id}/cancel", "post"): (
        "Cancelar pago",
        "Cancela un pago PENDING o APPROVED. Acepta un motivo opcional.",
        {404: "Pago no encontrado", 409: "El pago no está abierto"},
    ),
    ("/api/payments/{payment_id}/execute", "post"): (
        "Efectuar pago",
        "Descuenta el monto de la cuenta y del saldo pendiente del gasto. "
        "Si el saldo llega a cero, el gasto pasa a PAID.",
        {
            404: "Pago no encontrado",
            409: "Pago o gasto no aprobado, monto excede el saldo pendiente o saldo insuficiente",
        },
    ),
    ("/api/accounts", "get"): (
        "Listar cuentas",
        "Cuentas bancarias paginadas con `limit` y `offset`.",
        {},
    ),
    ("/api/accounts/{account_id}", "get"): (
        "Obtener cuenta",
        "Devuelve una cuenta bancaria por su ID.",
        {404: "Cuenta no encontrada"},
    ),
    ("/api/accounts", "post"): (
        "Crear cuenta",
        "Registra una cuenta bancaria. Saldo inicial por defecto 0.00, moneda por defecto MXN.",
        {409: "Datos obligatorios faltantes, número de cuenta duplicado o saldo negativo"},
    ),
    ("/api/accounts/{account_id}/deposit", "post"): (
        "Depositar",
        "Suma el monto al saldo de la cuenta.",
        {404: "Cuenta no encontrada", 409: "El depósito debe ser mayor a cero"},
    ),
    ("/api/users", "get"): (
        "Listar usuarios",
        "Usuarios paginados con `limit` y `offset`.",
        {},
    ),
    ("/api/users/{user_id}", "get"): (
        "Obtener usuario",
        "Devuelve un usuario por su ID.",
        {404: "Usuario no encontrado"},
    ),
    ("/api/users", "post"): (
        "Crear usuario",
        "Registra un usuario con un rol existente. La contraseña se guarda hasheada.",
        {404: "Rol no encontrado", 409: "El correo ya está registrado"},
    ),
}

ERROR_REF = {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorOut"}}}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description="API para registrar gastos, aprobarlos y pagarlos desde cuentas bancarias.",
        routes=app.routes,
    )
    components = schema.setdefault("components", {})
    components.setdefault("schemas", {})["ErrorOut"] = {
        "title": "ErrorOut",
        "type": "object",
        "properties": {"detail": {"title": "Detail", "type": "string"}},
        "required": ["detail"],
    }
    components["securitySchemes"] = {
        "basicAuth": {
            "type": "http",
            "scheme": "basic",
            "description": "Correo y contraseña del usuario.",
        }
    }
    schema["security"] = [{"basicAuth": []}]

    for (path, method), (summary, description, error_codes) in API_DOCS.items():
        operation = schema["paths"][path][method]
        operation["summary"] = summary
        operation["description"] = description
        responses = operation.setdefault("responses", {})
        responses["401"] = {"description": "Credenciales inválidas o ausentes", "content": ERROR_REF}
        for code, text in error_codes.items():
            responses[str(code)] = {"description": text, "content": ERROR_REF}

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
