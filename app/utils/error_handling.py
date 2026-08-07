from fastapi import HTTPException


def raise_db_error(e: Exception):
    """
    Turn an unexpected exception into a client-safe HTTPException.

    The real exception text (which can include DB driver/schema detail) is
    logged server-side only; clients get a generic message so internals
    aren't disclosed. Known "DB unreachable" errors still map to a clear 503.
    """
    error_str = str(e)
    print(f"[ERROR] {error_str}")
    if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
        raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
    raise HTTPException(status_code=500, detail="An internal server error occurred. Please try again later.")
