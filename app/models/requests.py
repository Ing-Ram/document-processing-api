from pathlib import Path
from pydantic import BaseModel, Field, field_validator

from app.models.enums import ProcessType


class CreateJobRequest(BaseModel):
    filename: str = Field(
        min_length=1,
        max_length=255,
        examples=["customers.csv"],
    )

    process_type: ProcessType

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, filename: str)-> str:
        cleaned_filename = filename.strip()

        if not cleaned_filename:
            raise ValueError("Filename cannot be empty.")

        extension = Path(cleaned_filename).suffix.lower()
        if extension != ".csv":
            raise ValueError("Only CSV files are supported.")

        return cleaned_filename

    