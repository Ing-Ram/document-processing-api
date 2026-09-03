from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path

from fastapi import UploadFile, File


from app.models.requests import CreateJobRequest, ProcessJobRequest
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_job_service, get_storage_service
from app.models.enums import JobStatus
from app.models.requests import CreateJobRequest
from app.models.responses import JobResponse
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.services.storage_service import StorageService



from app.dependencies import (
    get_job_service,
    get_storage_service,
    get_processing_service,
)

from app.services.processing_service import ProcessingService


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


# @router.post(
#     "/{job_id}/process",
#     response_model=JobResponse,
# )
def process_job(
    job_id: str,
    request: ProcessJobRequest,
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    
    output_directory = Path("tmp/processed") / job_id
    output_path = output_directory / "cleaned.csv"
    error_path = output_directory / "rejected.csv"
    
    job = service.process_job(
        job_id=job_id,
        input_path=request.input_path,
        output_path=output_path,
        error_path=error_path,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found.",
        )

    return job


@router.post(
    "/{job_id}/upload",
    response_model=JobResponse,
)

async def upload_job_file(
    job_id: str,
    file: UploadFile = File(...),
    service: JobService = Depends(get_job_service),
    storage: StorageService = Depends(get_storage_service),


) -> JobResponse:
    job=service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found.",
        )


    if file.filename is None or not file.filename.lower().endswith(".csv"):
        raise HTTPException (
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported.",
    )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV file is empty.",
        )

    storage.save_upload(
        job_id=job_id,
        contents=contents,
    )



    updated_job = service.mark_job_ready(job_id)

    if updated_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job with ID {job_id} not found."
        )

    return updated_job



@router.post(
    "/{job_id}/process",
    response_model=JobResponse,
)
def process_job(
    job_id: str,
    processing_service: ProcessingService = Depends(
        get_processing_service
    ),
) -> JobResponse:
    job = processing_service.process_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found.",
        )

    return job