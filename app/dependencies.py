from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.services.storage_service import StorageService



job_repository = JobRepository()


def get_job_service() -> JobService:
    return JobService(job_repository)


storage_service = StorageService()

def get_storage_service() -> StorageService:
    return storage_service


