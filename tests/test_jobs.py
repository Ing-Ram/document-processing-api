import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.dependencies import get_job_service
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.models.requests import CreateJobRequest
from app.models.enums import JobStatus, ProcessType

from app.main import app

test_repository = JobRepository()

def override_get_job_service() -> JobService:
    return JobService(test_repository)

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_test_repository():
    global test_repository
    test_repository = JobRepository()
    yield

def test_create_job_returns_created_job() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "customers.csv",
            "process_type": "customer_csv_cleanup",
        },
    )

    print(response.json())

    assert response.status_code == 201
    assert response.json()["filename"] == "customers.csv"
    # assert response.status_code == 201, response.text

    response_body = response.json()
    # print(response.json())

    assert response_body["job_id"]
    assert response_body["filename"] == "customers.csv"
    assert response_body["process_type"] == "customer_csv_cleanup"
    assert response_body["status"] == "AWAITING_UPLOAD"
    assert response_body["created_at"]
    assert response_body["updated_at"] is None
    assert response_body["completed_at"] is None



def test_get_job_returns_existing_job() -> None:
    create_response = client.post(
        "/jobs",
        json={
            "filename": "customers.csv",
            "process_type": "customer_csv_cleanup",
        },
    )

    job_id = create_response.json()["job_id"]

    get_response = client.get(f"/jobs/{job_id}")

    assert get_response.status_code == 200
    assert get_response.json()["job_id"] == job_id
    assert get_response.json()["filename"] == "customers.csv"


def test_get_job_returns_404_for_missing_job() -> None:
    response = client.get("/jobs/missing-job-id")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Job with ID missing-job-id not found.",
    }



def test_create_job_rejects_invalid_process_type() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "customers.csv",
            "process_type": "unsupported_process",
        },
    )

    assert response.status_code == 422

def test_creat_job_accepts_uppercase_csv_extension() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "customers.CSV",
            "process_type": "customer_csv_cleanup",
        },
    )
    assert response.status_code == 201
    assert response.json()["filename"] == "customers.CSV"

def test_create_job_removes_filename_whitespace() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "  customers.csv  ",
            "process_type": "customer_csv_cleanup",
        },
    )
    assert response.status_code == 201
    assert response.json()["filename"] == "customers.csv"

# def test_create_job_rejects_non_csv_file() -> None:
#     response = client.post(
#         "/jobs",
#         json={
#             "filename": "customers.pdf",
#             "process_type": "customer_csv_cleanup",
#         },
#     )

#     assert response.status_code == 422

def test_create_job_rejects_non_csv_file() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "customers.pdf",
            "process_type": "customer_csv_cleanup",
        },
    )

    assert response.status_code == 422

    response_body = response.json()

    assert response_body["detail"][0]["msg"] == (
        "Value error, Only CSV files are supported."
    )

def test_create_job_rejects_filename_without_extension() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "customers",
            "process_type": "customer_csv_cleanup",
        },
    )

    assert response.status_code == 422


def test_create_job_rejects_empty_filename() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "",
            "process_type": "customer_csv_cleanup",
        },
    )

    assert response.status_code == 422


def test_process_job_returns_404_for_missing_job(tmp_path) -> None:
    response = client.post(
        "/jobs/missing-job/process",
        json={
            "input_path": str(tmp_path / "input.csv"),
            "output_path": str(tmp_path / "output.csv"),
            "error_path": str(tmp_path / "errors.csv"),
        },
    )

    assert response.status_code == 404



def test_create_job_rejects_whitespace_only_filename() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "   ",
            "process_type": "customer_csv_cleanup",
        },
    )

    assert response.status_code == 422


   



def test_upload_rejects_non_csv_file() -> None:
    create_response = client.post(
        "/jobs",
        json={
            "filename": "customers.csv",
            "process_type": "customer_csv_cleanup",
        },
    )

    job_id = create_response.json()["job_id"]

    response = client.post(
        f"/jobs/{job_id}/upload",
        files={
            "file": (
                "customers.txt",
                "hello",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only CSV files are supported."
    }


def test_upload_rejects_empty_csv() -> None:
    create_response = client.post(
        "/jobs",
        json={
            "filename": "customers.csv",
            "process_type": "customer_csv_cleanup",
        },
    )

    job_id = create_response.json()["job_id"]

    response = client.post(
        f"/jobs/{job_id}/upload",
        files={
            "file": (
                "customers.csv",
                "",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Uploaded CSV file is empty."
    }


def test_upload_csv_marks_job_ready() -> None:
    create_response = client.post(
        "/jobs",
        json={
            "filename": "customers.csv",
            "process_type": "customer_csv_cleanup",
        },
    )

    job_id = create_response.json()["job_id"]

    csv_data = (
        "customer_id,first_name,last_name,email\n"
        "1001,Chad,Ingram,chad@example.com\n"
    )

    response = client.post(
        f"/jobs/{job_id}/upload",
        files={
            "file": (
                "customers.csv",
                csv_data,
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "READY"
    assert body["records_received"] is None
    assert body["completed_at"] is None


def test_mark_job_ready_updates_status() -> None:
    repository = JobRepository()
    service = JobService(repository)

    request = CreateJobRequest(
        filename="customers.csv",
        process_type=ProcessType.CUSTOMER_CSV_CLEANUP,
    )

    job = service.create_job(request)

    updated_job = service.mark_job_ready(job.job_id)

    assert updated_job is not None
    assert updated_job.status == JobStatus.READY
    assert updated_job.updated_at is not None


def test_process_ready_job_completes_job(tmp_path: Path) -> None:
    repository = JobRepository()
    service = JobService(repository)

    request = CreateJobRequest(
        filename="customers.csv",
        process_type=ProcessType.CUSTOMER_CSV_CLEANUP,
    )

    job = service.create_job(request)
    service.mark_job_ready(job.job_id)

    input_file = tmp_path / "customers.csv"
    output_file = tmp_path / "cleaned.csv"
    error_file = tmp_path / "rejected.csv"

    input_file.write_text(
        "customer_id,first_name,last_name,email\n"
        "1001,Chad,Ingram,chad@example.com\n"
    )

    completed_job = service.process_ready_job(
        job_id=job.job_id,
        input_path=input_file,
        output_path=output_file,
        error_path=error_file,
    )

    assert completed_job is not None
    assert completed_job.status == JobStatus.COMPLETED
    assert completed_job.records_received == 1
    assert completed_job.records_processed == 1
    assert output_file.exists()



def test_process_ready_job_does_not_process_unready_job(tmp_path: Path) -> None:
    repository = JobRepository()
    service = JobService(repository)

    request = CreateJobRequest(
        filename="customers.csv",
        process_type=ProcessType.CUSTOMER_CSV_CLEANUP,
    )

    job = service.create_job(request)

    result = service.process_ready_job(
        job_id=job.job_id,
        input_path=tmp_path / "input.csv",
        output_path=tmp_path / "cleaned.csv",
        error_path=tmp_path / "rejected.csv",
    )

    assert result is not None
    assert result.status == JobStatus.AWAITING_UPLOAD
