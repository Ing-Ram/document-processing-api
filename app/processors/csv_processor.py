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

			rows = [ self._clean_row(row)
			for row in reader
			]
		valid_rows = []
		rejected_rows = []

		for row in rows:
			if self._is_valid_email(row["email"]):
				valid_rows.append(row)
			else:
				rejected_rows.append(rows)


		return ProcessingResult(
			records_received=len(rows),
			records_processed=len(valid_rows),
			records_rejected=len(rejected_rows),
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
	
	def _clean_row(self, row: dict[str,str]) -> dict[str, str]:
		cleaned_row =  {
			key: value.strip()
			for key, value in row.items()
		}

		cleaned_row["email"] = cleaned_row["email"].lower()
		return cleaned_row

	def _is_valid_email(self, email: str) -> bool:
		return "@" in email and "." in email.split("@")[-1] 
