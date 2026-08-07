import bcrypt

_BCRYPT_PREFIXES = ("$2a$", "$2b$", "$2y$")


def is_hashed(value: str) -> bool:
    return bool(value) and value.startswith(_BCRYPT_PREFIXES)


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, stored_value: str) -> bool:
    """
    Verify a plaintext password against what's stored in `password_hash`.

    Rows created before hashing was added still hold the raw password, so a
    stored value without a bcrypt prefix is compared directly. Callers that
    match on that legacy path should immediately re-hash and persist the
    value to migrate the row off plaintext (see login_user in
    user_registration.py).
    """
    if not stored_value:
        return False
    if is_hashed(stored_value):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), stored_value.encode("utf-8"))
        except ValueError:
            return False
    return plain_password == stored_value
