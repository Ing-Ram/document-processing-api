import csv
from pathlib import Path


from app.models.processing import ProcessingResult

REQUIRED_COLUMNS = {
	"customer_id",
	"first_name",
	"last_name",
	"email",
}


class CsvProcessor:

	def process(self, input_path: Path) -> ProcessingResult:
		with input_path.open(
			mode="r",
			newline="",
			encoding="utf-8",
		
		) as csv_file:
			
			reader = csv.DictReader(csv_file)


			self._validate_columns(reader.fieldnames)

			rows = list(reader)
		


		return ProcessingResult(
			records_received=len(rows),
			records_processed=len(rows),
			records_rejected=0,
			duplicate_records=0

		)




	def _validate_columns(
		self,
		fieldnames: list[str] | None,
	) -> None:

		if fieldnames is None:
			raise ValueError("ERROR: CSV file does not contain a header row.")
		
		columns = set(fieldnames)

		missing_columns = REQUIRED_COLUMNS - columns

		if missing_columns:
			missing = ", ".join(sorted(missing_columns))

			raise ValueError(
				f"ERROR: CSV file is missing required columns: {missing}"
			)

