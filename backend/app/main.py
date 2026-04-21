from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.access import router as access_router
from app.models import log_acces


app = FastAPI(
    title="Système de gestion d’accès et de réservation"
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(access_router)