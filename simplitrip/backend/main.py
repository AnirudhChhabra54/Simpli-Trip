# """
# SimpliTrip Backend - Main FastAPI Application
# """
# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from contextlib import asynccontextmanager
# import time

# from config.settings import settings
# from api.routes import router
# from services.model_service import model_service
# from utils.logger import logger


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """
#     Lifespan context manager for startup and shutdown events
#     """
#     # Startup
#     logger.info("Starting SimpliTrip Backend...")
#     logger.info(f"Environment: {settings.ENVIRONMENT}")
    
#     # Initialize model service
#     try:
#         model_service.initialize()
#         logger.info("Model service initialized successfully")
#     except Exception as e:
#         logger.error(f"Failed to initialize model service: {e}")
#         logger.warning("API will start but some features may not work")
    
#     yield
    
#     # Shutdown
#     logger.info("Shutting down SimpliTrip Backend...")


# # Create FastAPI app
# app = FastAPI(
#     title="SimpliTrip AI Backend",
#     description="AI-powered travel planning backend for SimpliTrip",
#     version="1.0.0",
#     lifespan=lifespan
# )


# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins_list,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # Add request timing middleware
# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     """Add processing time to response headers"""
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response


# # Global exception handler
# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     """Handle all unhandled exceptions"""
#     logger.error(f"Unhandled exception: {exc}", exc_info=True)
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "Internal server error",
#             "detail": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred"
#         }
#     )


# # Include API routes
# app.include_router(router, prefix=settings.API_V1_PREFIX)


# # Root endpoint
# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {
#         "message": "SimpliTrip AI Backend",
#         "version": "1.0.0",
#         "status": "running",
#         "docs": "/docs"
#     }


# if __name__ == "__main__":
#     import uvicorn
    
#     uvicorn.run(
#         "main:app",
#         host=settings.API_HOST,
#         port=settings.API_PORT,
#         reload=settings.API_RELOAD,
#         log_level=settings.LOG_LEVEL.lower()
#     )


'''
NEW file 06 / Dec/2025
'''
"""
SimpliTrip Backend - Main FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from config.settings import settings
from utils.logger import logger

# NOTE: we intentionally avoid importing `api.routes` and `services.model_service`
# at module import time to prevent import-time crashes when optional adapters
# (like ollama_service) are missing. They will be imported lazily inside lifespan.


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Lazy-imports and initializes model_service and routes to avoid import-time crashes.
    """
    logger.info("Starting SimpliTrip Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Lazy import of model_service (so missing optional deps won't crash at import)
    model_service = None
    try:
        from services.model_service import model_service as _ms
        model_service = _ms
        # initialize model service
        try:
            model_service.initialize()
            logger.info("Model service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize model service: {e}", exc_info=True)
            logger.warning("API will start but some features may not work")
    except Exception as e:
        # If import fails, log it and continue; routes may still be added but will
        # error at runtime if they depend on model_service.
        logger.error(f"Could not import services.model_service: {e}", exc_info=True)
        logger.warning("Continuing startup without model_service (some endpoints may fail)")

    # Lazy import and include API router after attempting to initialize services.
    try:
        from api.routes import router
        # If router already included, skip (safe). Otherwise include now.
        if not any(getattr(r, "path", "") == settings.API_V1_PREFIX for r in app.routes):
            app.include_router(router, prefix=settings.API_V1_PREFIX)
        logger.info("API routes included")
    except Exception as e:
        logger.error(f"Failed to import/include API routes: {e}", exc_info=True)
        logger.warning("Some API routes may not be available")

    yield

    # Shutdown
    logger.info("Shutting down SimpliTrip Backend...")
    try:
        if model_service and hasattr(model_service, "shutdown"):
            # call optional shutdown hook
            model_service.shutdown()
            logger.info("Model service shutdown complete")
    except Exception as e:
        logger.error("Error during model_service shutdown", exc_info=True)


# Create FastAPI app
app = FastAPI(
    title="SimpliTrip AI Backend",
    description="AI-powered travel planning backend for SimpliTrip",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SimpliTrip AI Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )


def main():
    """Console entry point used by setup.py (`simplitrip-backend=main:main`)."""
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )