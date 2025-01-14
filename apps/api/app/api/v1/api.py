from fastapi import APIRouter

from app.api.v1.endpoints import auth, exercises, workouts, profiles, measurements, chat

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
api_router.include_router(workouts.router, prefix="/workouts", tags=["Workouts"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["User Profiles"])
api_router.include_router(measurements.router, prefix="/measurements", tags=["Body Measurements"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"]) 