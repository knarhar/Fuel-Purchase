from fastapi.routing import APIRouter

from app.routers.endpoints import admin, purchase

api_router = APIRouter()

api_router.include_router(admin.router, prefix="/admin")
api_router.include_router(purchase.router, prefix="/purchases")
