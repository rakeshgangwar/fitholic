from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

# Initialize logging
logger = get_logger(__name__)
setup_logging()

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
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600  # Cache preflight requests for 10 minutes
)

@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return JSONResponse(content={"status": "ok"})

app.include_router(api_router, prefix=settings.API_V1_STR)
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Fitholic API")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Fitholic API")

