from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.access import router as access_router
from app.routers.reservation import router as reservation_router
from app.routers.notification import router as notification_router
from app.routers.notification import router as notification_router


# modèles importés UNE SEULE FOIS (sans Notification)

app = FastAPI()

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(access_router)
app.include_router(reservation_router)
app.include_router(notification_router)
