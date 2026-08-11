from typing import Dict, Optional

from app.models.responses import JobResponse


class JobRepository:
    def __init__(self) -> None:
        self._jobs: Dict[str, JobResponse] = {}

    def save(self, job: JobResponse) -> JobResponse:
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> Optional[JobResponse]:
        return self._jobs.get(job_id)


job_repository = JobRepository()