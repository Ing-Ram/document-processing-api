from pathlib import Path


class StorageService:
    def get_input_path(self, job_id: str) -> Path:
        return Path("tmp/uploads") / job_id / "input.csv"

    def get_output_path(self, job_id: str) -> Path:
        return Path("tmp/processed") / job_id / "cleaned.csv"

    def get_error_path(self, job_id: str) -> Path:
        return Path("tmp/processed") / job_id / "rejected.csv"


    def save_upload(
        self, 
        job_id: str,
        contents: bytes,
    ) -> Path:
        input_path = self.get_input_path(job_id)


        input_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        input_path.write_bytes(contents)

        return input_path