from app.models.enums import JobStatus, ProcessType
from app.models.requests import CreateJobRequest
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.services.processing_service import ProcessingService
from app.services.storage_service import StorageService


def test_processing_service_processes_ready_job(tmp_path) -> None:
    repository = JobRepository()
    job_service = JobService(repository)
    storage_service = StorageService()

    storage_service.get_input_path = lambda job_id: (
        tmp_path / job_id / "input.csv"
    )
    storage_service.get_output_path = lambda job_id: (
        tmp_path / job_id / "cleaned.csv"
    )
    storage_service.get_error_path = lambda job_id: (
        tmp_path / job_id / "rejected.csv"
    )

    processing_service = ProcessingService(
        job_service=job_service,
        storage_service=storage_service,
    )

    job = job_service.create_job(
        CreateJobRequest(
            filename="customers.csv",
            process_type=ProcessType.CUSTOMER_CSV_CLEANUP,
        )
    )

    input_path = storage_service.get_input_path(job.job_id)
    input_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    input_path.write_text(
        "customer_id,first_name,last_name,email\n"
        "1001,Chad,Ingram,chad@example.com\n",
        encoding="utf-8",
    )

    job_service.mark_job_ready(job.job_id)

    result = processing_service.process_job(job.job_id)

    assert result is not None
    print(result.error_message)
    assert result.status == JobStatus.COMPLETED
    assert result.records_received == 1
    assert result.records_processed == 1