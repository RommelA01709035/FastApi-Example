import hashlib
import hmac
import os
import secrets
import time

import bcrypt

BCRYPT_ROUNDS = 12
BCRYPT_MAX_BYTES = 72  # bcrypt ignores anything past 72 bytes; truncate like pgcrypto does

SESSION_COOKIE = "session"
SESSION_MAX_AGE = 8 * 60 * 60
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)


def _password_bytes(plain: str) -> bytes:
    return plain.encode()[:BCRYPT_MAX_BYTES]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_password_bytes(plain), bcrypt.gensalt(BCRYPT_ROUNDS)).decode()


def verify_password(plain: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_password_bytes(plain), password_hash.encode())
    except ValueError:  # malformed or non-bcrypt hash
        return False


def _sign(payload: str) -> str:
    return hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()


def create_session_token(user_id: int) -> str:
    payload = f"{user_id}.{int(time.time()) + SESSION_MAX_AGE}"
    return f"{payload}.{_sign(payload)}"


def read_session_token(token: str | None) -> int | None:
    try:
        user_id, expires, signature = (token or "").split(".")
        if not hmac.compare_digest(signature, _sign(f"{user_id}.{expires}")):
            return None
        if int(expires) < time.time():
            return None
        return int(user_id)
    except ValueError:
        return None
