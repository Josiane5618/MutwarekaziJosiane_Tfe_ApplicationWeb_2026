from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.bootstrap import bootstrap_database
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.access import router as access_router
from app.routers.reservation import router as reservation_router
from app.routers.notification import router as notification_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_database_tables():
    bootstrap_database()


@app.get("/health", tags=["Health"])
def healthcheck():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(access_router)
app.include_router(reservation_router)
app.include_router(notification_router)
