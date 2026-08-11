from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.models.enums import JobStatus
from app.models.requests import CreateJobRequest
from app.models.responses import JobResponse
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]    
)


repository = JobRepository()
service = JobService(repository)

@router.post(
    "", 
    response_model=JobResponse, 
    status_code=status.HTTP_201_CREATED,
)

def create_job(request: CreateJobRequest) -> JobResponse:
    return service.create_job(request)



@router.get(
    "/{job_id}", 
    response_model=JobResponse,
)


def get_job(job_id: str) -> JobResponse:
    job = service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found.",
        )
    return job 