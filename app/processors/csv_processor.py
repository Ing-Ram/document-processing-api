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

	def process(
		self, 
		input_path: Path,
		output_path: Path | None = None,
		error_path: Path | None = None,	
	) -> ProcessingResult:
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
		duplicate_rows = []

		seen_emails = set()
		
		for row in rows:
			email = row["email"]

			
			if not self._is_valid_email(email):
				rejected_row = row.copy()
				rejected_row["rejection_reason"] = "Invalid email address"
				rejected_rows.append(rejected_row)
				continue
			if email in seen_emails:
				duplicate_rows.append(row)
				continue
			seen_emails.add(email)
			valid_rows.append(row)

		if output_path is not None:
			self._write_output(
				output_path=output_path,
				rows=valid_rows,
			)
		

		if error_path is not None and rejected_rows:
			self._write_error_output(
				error_path=error_path,
				rows=rejected_rows,
			)




		if output_path is not None:
			self._write_output(
				output_path=output_path,
				rows=valid_rows,
		)
		
		



		return ProcessingResult(
			records_received=len(rows),
			records_processed=len(valid_rows),
			records_rejected=len(rejected_rows),
			duplicate_records=len(duplicate_rows),
			output_path=output_path,
			error_path=error_path if rejected_rows else None,
		)
	def _write_error_output(
		self,
		error_path: Path,
		rows: list[dict[str, str]],
	) -> None:
		error_path.parent.mkdir(
			parents=True,
			exist_ok=True,
		)

		with error_path.open(
			mode="w",
			newline="",
			encoding="utf-8",
		) as csv_file:

			writer = csv.DictWriter(
				csv_file,
				fieldnames=[
					"customer_id",
					"first_name",
					"last_name",
					"email",
					"rejection_reason",
				],
			)

			writer.writeheader()
			writer.writerows(rows)
	def _write_output(
		self,
		output_path: Path,
		rows: list[dict[str, str]],
	) -> None:
		output_path.parent.mkdir(
			parents=True,
			exist_ok=True,
		)

		with output_path.open(
			mode="w",
			newline="",
			encoding="utf-8",
		) as csv_file:
			
			writer = csv.DictWriter(
				csv_file,
				fieldnames=[
					"customer_id",
					"first_name",
					"last_name",
					"email",
				],
			)

			writer.writeheader()
			writer.writerows(rows)


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
