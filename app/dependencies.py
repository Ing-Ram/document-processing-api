from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService


job_repository = JobRepository()


def get_job_service() -> JobService:
    return JobService(job_repository)
