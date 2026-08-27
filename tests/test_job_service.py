from pathlib import Path
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

def test_process_job_marks_job_completed(tmp_path: Path) -> None:
    repository = JobRepository()
    service = JobService(repository)

    request = CreateJobRequest(
        filename="customers.csv",
        process_type=ProcessType.CUSTOMER_CSV_CLEANUP,
    )

    job = service.create_job(request)

    input_file = tmp_path / "customers.csv"
    output_file = tmp_path / "cleaned.csv"
    error_file = tmp_path / "rejected.csv"

    input_file.write_text(
        "customer_id,first_name,last_name,email\n"
        "1001,Chad,Ingram,chad@example.com\n"
    )

    completed_job = service.process_job(
        job_id=job.job_id,
        input_path=input_file,
        output_path=output_file,
        error_path=error_file,
    )

    assert completed_job is not None
    assert completed_job.status == JobStatus.COMPLETED
    assert completed_job.records_received == 1
    assert completed_job.records_processed == 1
    assert completed_job.records_rejected == 0
    assert completed_job.duplicate_records == 0
    assert completed_job.completed_at is not None
    assert output_file.exists()


def test_process_job_marks_job_failed_for_invalid_csv(tmp_path: Path) -> None:
    repository = JobRepository()
    service = JobService(repository)

    request = CreateJobRequest(
        filename="customers.csv",
        process_type=ProcessType.CUSTOMER_CSV_CLEANUP,
    )

    job = service.create_job(request)

    input_file = tmp_path / "bad.csv"
    output_file = tmp_path / "cleaned.csv"
    error_file = tmp_path / "rejected.csv"

    input_file.write_text(
        "customer_id,name,email\n"
        "1001,Chad Ingram,chad@example.com\n"
    )

    failed_job = service.process_job(
        job_id=job.job_id,
        input_path=input_file,
        output_path=output_file,
        error_path=error_file,
    )

    assert failed_job is not None
    assert failed_job.status == JobStatus.FAILED
    assert failed_job.error_message is not None
    assert "missing required columns" in failed_job.error_message
    assert failed_job.completed_at is None