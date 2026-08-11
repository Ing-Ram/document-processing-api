from app.models.enums import JobStatus, ProcessType
from app.models.requests import CreateJobRequest
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService


def test_create_job_generates_job_record() -> None:
    repository = JobRepository()
    service = JobService(repository)

    request = CreateJobRequest(
        filename="customers.csv",
        process_type=ProcessType.CUSTOMER_CSV_CLEANUP,
    )

    job = service.create_job(request)

    assert job.job_id
    assert job.filename == "customers.csv"
    assert job.process_type == ProcessType.CUSTOMER_CSV_CLEANUP
    assert job.status == JobStatus.AWAITING_UPLOAD
    assert job.created_at is not None
    assert job.updated_at is None
    assert job.completed_at is None


def test_create_job_saves_job_in_repository() -> None:
    repository = JobRepository()
    service = JobService(repository)

    request = CreateJobRequest(
        filename="customers.csv",
        process_type=ProcessType.CUSTOMER_CSV_CLEANUP,
    )

    created_job = service.create_job(request)
    stored_job = repository.get(created_job.job_id)

    assert stored_job is not None
    assert stored_job == created_job


def test_get_job_returns_existing_job() -> None:
    repository = JobRepository()
    service = JobService(repository)

    request = CreateJobRequest(
        filename="customers.csv",
        process_type=ProcessType.CUSTOMER_CSV_CLEANUP,
    )

    created_job = service.create_job(request)
    retrieved_job = service.get_job(created_job.job_id)

    assert retrieved_job is not None
    assert retrieved_job.job_id == created_job.job_id
    assert retrieved_job.filename == "customers.csv"


def test_get_job_returns_none_for_missing_job() -> None:
    repository = JobRepository()
    service = JobService(repository)

    result = service.get_job("missing-job-id")

    assert result is None