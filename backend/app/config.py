import os
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent


def load_env_file() -> None:
    for env_path in (BACKEND_DIR / ".env", PROJECT_DIR / ".env"):
        if not env_path.is_file():
            continue

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key:
                os.environ.setdefault(key, value)

        break


def get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)

    if value in (None, ""):
        return default

    try:
        return int(value)
    except ValueError:
        return default


def get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value in (None, ""):
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


load_env_file()

DATABASE_URL = get_env(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:change_me@localhost:5432/tfe_gestion_acces"
)
SQL_ECHO = get_bool_env("SQL_ECHO", False)

JWT_SECRET_KEY = get_env("JWT_SECRET_KEY", "CHANGE_ME_IN_ENV")
JWT_ALGORITHM = get_env("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = get_int_env(
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    60
)

API_HOST = get_env("API_HOST", "127.0.0.1")
API_PORT = get_int_env("API_PORT", 8000)
API_RELOAD = get_bool_env("API_RELOAD", True)
