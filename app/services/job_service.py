from pathlib import Path
from app.processors.csv_processor import CsvProcessor

from datetime import datetime, timezone
from uuid import uuid4

from app.models.enums import JobStatus
from app.models.requests import CreateJobRequest
from app.models.responses import JobResponse
from app.repositories.job_repository import JobRepository

class JobService:
    def __init__(
        self,
        repository: JobRepository,
        processor: CsvProcessor | None = None,
     ) -> None:
        self.repository = repository
        self.processor = processor or CsvProcessor()

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


    def process_job(
        self,
        job_id: str,
        input_path: Path,
        output_path: Path,
        error_path: Path,
    ) -> JobResponse | None:
        job = self.repository.get(job_id)

        if job is None: 
            return None

        now = datetime.now(timezone.utc)

        job.status = JobStatus.PROCESSING
        job.updated_at = now
        self.repository.update(job)

        try:

            result = self. processor.process(
                input_path=input_path,
                output_path=output_path,
                error_path=error_path       
            )

            job.status = JobStatus.COMPLETED
            job.updated_at = datetime.now(timezone.utc)
            job.completed_at = job.updated_at

            job.records_received = result.records_received
            job.records_processed = result.records_processed
            job.records_rejected = result.records_rejected
            job.duplicate_records = result.duplicate_records    
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.updated_at = datetime.now(timezone.utc)
            job.error_message = str(exc)

        return self.repository.update(job)