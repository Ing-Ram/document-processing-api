from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_job_returns_created_job() -> None:
    response = client.post(
        "/jobs",
        json={
            "filename": "customers.csv",
            "process_type": "customer_csv_cleanup",
        },
    )

    assert response.status_code == 201

    response_body = response.json()

    assert response_body["job_id"]
    assert response_body["filename"] == "customers.csv"
    assert response_body["process_type"] == "customer_csv_cleanup"
    assert response_body["status"] == "AWAITING_UPLOAD"
    assert response_body["created_at"]
    assert response_body["updated_at"]
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