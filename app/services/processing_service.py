from app.models.responses import JobResponse
from app.services.job_service import JobService
from app.services.storage_service import StorageService


# adding a processing coordinator so my API route no longer needs to know where input is 
class ProcessingService:
    def __init__(
        self,
        job_service: JobService,
        storage_service: StorageService,
    ) -> None:
        self.job_service = job_service
        self.storage_service = storage_service


    def process_job(
        self,
        job_id: str,

    ) -> JobResponse | None:
        input_path = self.storage_service.get_input_path(job_id)
        output_path = self.storage_service.get_output_path(job_id)
        error_path = self.storage_service.get_error_path(job_id)


        return self.job_service.process_ready_job(
            job_id = job_id,
            input_path=input_path,
            output_path=output_path,
            error_path=error_path,

        )