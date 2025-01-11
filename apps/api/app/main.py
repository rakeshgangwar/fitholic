from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="""
    Fitholic API helps you track your fitness journey and achieve your health goals.
    
    ## Features
    * User authentication and authorization
    * Profile management
    * Workout tracking
    * Progress monitoring
    
    ## Authentication
    All authenticated endpoints require a valid JWT token in the Authorization header.
    """
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, settings.WEBAPP_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return JSONResponse(content={"status": "ok"})

app.include_router(api_router, prefix=settings.API_V1_STR)
