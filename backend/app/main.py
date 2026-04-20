from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router

app = FastAPI(
    title="Application de gestion d’accès et de réservation",
    version="1.0"
)

app.include_router(auth_router)
app.include_router(admin_router)