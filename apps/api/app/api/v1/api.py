from fastapi import APIRouter

from app.api.v1.endpoints import auth, exercises, workouts

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
api_router.include_router(workouts.router, prefix="/workouts", tags=["Workouts"]) 