from pydantic import BaseModel


class ProcessingResult(BaseModel):
	records_received: int
	records_processed: int
	records_rejected: int
	duplicate_records: int
