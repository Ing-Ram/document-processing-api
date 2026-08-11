from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router

def create_app() -> FastAPI:
    application = FastAPI(
        title="Document Processing API", 
        description="A simple API for submitting and tracking document-processing jobs.",
        version="0.1.0",
    )
    application.include_router(health_router)
    application.include_router(jobs_router)

    return application

app = create_app()

