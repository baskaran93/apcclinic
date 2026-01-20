INSTALLED_APPS = [
    "corsheaders"
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware"
]

CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins (For testing only)
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]  # Allow OPTIONS
CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]  # Allow required headers
