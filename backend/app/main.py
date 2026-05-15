from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bootstrap import bootstrap_database
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.access import router as access_router
from app.routers.face_detection import router as face_detection_router
from app.routers.reservation import router as reservation_router
from app.routers.notification import router as notification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_database()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def healthcheck():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(access_router)
app.include_router(face_detection_router)
app.include_router(reservation_router)
app.include_router(notification_router)
