from datetime import datetime, timezone
from uuid import uuid4

from app.models.requests import CreateJobRequest, ProcessJobRequest
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_job_service
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

def create_job(
    request: CreateJobRequest,
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    return service.create_job(request)



@router.get(
    "/{job_id}", 
    response_model=JobResponse,
)


def get_job(
    job_id: str,
    service: JobService = Depends(get_job_service),		
) -> JobResponse:
    job = service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found.",
        )
    return job


@router.post(
    "/{job_id}/process",
    response_model=JobResponse,
)
def process_job(
    job_id: str,
    request: ProcessJobRequest,
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    job = service.process_job(
        job_id=job_id,
        input_path=request.input_path,
        output_path=request.output_path,
        error_path=request.error_path,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found.",
        )

    return job

