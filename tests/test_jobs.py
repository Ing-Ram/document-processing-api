import pytest
from fastapi.testclient import TestClient
from app.dependencies import get_job_service
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService

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

def test_create_job_rejects_whitespace_only_filename() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "   ",
            "process_type": "customer_csv_cleanup",
        },
    )

    assert response.status_code == 422



