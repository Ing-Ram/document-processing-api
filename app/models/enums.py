from enum import Enum


class JobStatus(str, Enum):
    AWAITING_UPLOAD = "AWAITING_UPLOAD"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ProcessType(str, Enum):
    CUSTOMER_CSV_CLEANUP = "customer_csv_cleanup"
    