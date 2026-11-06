from contextlib import asynccontextmanager
from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers import admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Fuel Purchase API", lifespan=lifespan)
app.include_router(admin.router)