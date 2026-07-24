from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.models.enums import JobStatus
from app.models.requests import CreateJobRequest
from app.models.responses import JobResponse
from app.repositories.job_repository import job_repository


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]    
)


@router.post(
    "", 
    response_model=JobResponse, status_code=status.HTTP_201_CREATED,
)

def create_job(request: CreateJobRequest) -> JobResponse:
    now = datetime.now(timezone.utc)

    job = JobResponse(
        job_id=str(uuid4()),
        filename=request.filename,
        process_type=request.process_type,
        status=JobStatus.AWAITING_UPLOAD,
        created_at=now,
        updated_at=now,
    )

    return job_repository.create(job)

@router.get(
    "/{job_id}", 
    response_model=JobResponse,
)
def get_job(job_id: str) -> JobResponse:
    job = job_repository.get_by_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found.",
        )
    return job 