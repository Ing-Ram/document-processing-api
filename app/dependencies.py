from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.services.storage_service import StorageService
from app.services.processing_service import ProcessingService



job_repository = JobRepository()


def get_job_service() -> JobService:
    return JobService(job_repository)


storage_service = StorageService()

def get_storage_service() -> StorageService:
    return storage_service

def get_processing_service() -> ProcessingService:
    return ProcessingService(
        job_service=get_job_service(),
        storage_service=get_storage_service(),
    )


