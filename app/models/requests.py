from pydantic import BaseModel, Field

from app.models.enums import ProcessType


class CreateJobRequest(BaseModel):
    filename: str = Field(
        min_length=1,
        max_length=255,
        examples=["customers.csv"],
    )

    process_type: ProcessType