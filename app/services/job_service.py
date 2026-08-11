from datetime import datetime, timezone
from uuid import uuid4

from app.models.enums import JobStatus
from app.models.requests import CreateJobRequest
from app.models.responses import JobResponse
from app.repositories.job_repository import JobRepository

class JobService:
    def __init__(self, job_repository: JobRepository):
        self.repository = job_repository

    def create_job(self, request: CreateJobRequest) -> JobResponse:
        job = JobResponse(
            job_id=str(uuid4()),
            filename=request.filename,
            process_type=request.process_type,
            status=JobStatus.AWAITING_UPLOAD,
            created_at=datetime.now(timezone.utc),
            updated_at=None
        )

        return self.repository.save(job)

    def get_job(self, job_id: str) -> JobResponse | None:
        return self.repository.get(job_id)  