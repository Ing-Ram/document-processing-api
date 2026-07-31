# Document Processing API

A simple FastAPI service for submitting and tracking document-processing jobs.

## Features

- Submit a document-processing job for a given file and process type
- Fetch job status and metadata by job ID
- Health check endpoint

## Requirements

- Python 3.11+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs are served at `http://127.0.0.1:8000/docs`.

## Running tests

```bash
pytest
```

## API Overview

### `GET /health`

Returns service health status.

### `POST /jobs`

Creates a new document-processing job.

**Request body:**

```json
{
  "filename": "customers.csv",
  "process_type": "customer_csv_cleanup"
}
```

**Response:** `201 Created` with the created job, including its `job_id` and initial status of `AWAITING_UPLOAD`.

### `GET /jobs/{job_id}`

Returns the job with the given ID, or `404` if it doesn't exist.

**Job statuses:** `AWAITING_UPLOAD`, `QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`

## Project Structure

```
app/
  api/routes/      # FastAPI routers (health, jobs)
  models/          # Pydantic request/response models and enums
  repositories/     # In-memory job storage
tests/             # Pytest test suite
```
