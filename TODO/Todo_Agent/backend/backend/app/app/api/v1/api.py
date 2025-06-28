from fastapi import APIRouter
from app.api.v1.endpoints import (
    weather, 
    Todo   
)

api_router = APIRouter()
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(Todo.router, prefix="/todo", tags=["todo"])
