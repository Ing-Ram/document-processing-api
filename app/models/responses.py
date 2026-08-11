from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import JobStatus, ProcessType


class JobResponse(BaseModel):
    job_id: str
    filename: str
    process_type: ProcessType
    status: JobStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: Optional[datetime] = None