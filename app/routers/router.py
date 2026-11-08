from fastapi.routing import APIRouter

from app.routers.endpoints import admin

api_router = APIRouter()

api_router.include_router(admin.router, prefix="/admin")
