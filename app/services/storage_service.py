from pathlib import Path


class StorageService:
    def get_input_path(self, job_id: str) -> Path:
        return Path("tmp/uploads") / job_id / "input.csv"

    def get_output_path(self, job_id: str) -> Path:
        return Path("tmp/processed") / job_id / "cleaned.csv"

    def get_error_path(self, job_id: str) -> Path:
        return Path("tmp/processed") / job_id / "rejected.csv"


    