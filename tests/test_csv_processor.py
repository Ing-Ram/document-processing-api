from pathlib import Path

import pytest

from app.processors.csv_processor import CsvProcessor


FIXTURES = Path(__file__).parent / "fixtures"


def test_processor_counts_valid_records() -> None:
    processor = CsvProcessor()

    result = processor.process(
        FIXTURES / "valid_customers.csv"
    )

    assert result.records_received == 3
    assert result.records_processed == 3
    assert result.records_rejected == 0
    assert result.duplicate_records == 0


def test_processor_rejects_missing_required_columns() -> None:
    processor = CsvProcessor()

    with pytest.raises(
        ValueError,
        match="CSV file is missing required columns",
    ):
        processor.process(
            FIXTURES / "missing_columns.csv"
        )


def test_processor_trims_row_whitespace() -> None:
    processor = CsvProcessor()

    row = {
        "customer_id": " 1001 ",
        "first_name": "  Chad  ",
        "last_name": " Ingram ",
        "email": " chad@example.com ",
    }

    cleaned = processor._clean_row(row)

    assert cleaned["customer_id"] == "1001"
    assert cleaned["first_name"] == "Chad"
    assert cleaned["last_name"] == "Ingram"
    assert cleaned["email"] == "chad@example.com"



def test_processor_trims_row_whitespace() -> None:
    processor = CsvProcessor()

    row = {
        "customer_id": " 1001 ",
        "first_name": "  Chad  ",
        "last_name": " Ingram ",
        "email": " chad@example.com ",
    }

    cleaned = processor._clean_row(row)

    assert cleaned["customer_id"] == "1001"
    assert cleaned["first_name"] == "Chad"
    assert cleaned["last_name"] == "Ingram"
    assert cleaned["email"] == "chad@example.com"



def test_processor_normalizes_email_to_lowercase() -> None:
    processor = CsvProcessor()

    row = {
        "customer_id": "1001",
        "first_name": "Chad",
        "last_name": "Ingram",
        "email": " CHAD@EXAMPLE.COM ",
    }

    cleaned = processor._clean_row(row)

    assert cleaned["email"] == "chad@example.com"




def test_processor_rejects_invalid_email_rows() -> None:
    processor = CsvProcessor()

    result = processor.process(
        FIXTURES / "invalid_email.csv"
    )

    assert result.records_received == 3
    assert result.records_processed == 2
    assert result.records_rejected == 1
    assert result.duplicate_records == 0


def test_email_validation() -> None:
    processor = CsvProcessor()

    assert processor._is_valid_email("chad@example.com") is True
    assert processor._is_valid_email("not-an-email") is False
    assert processor._is_valid_email("") is False


def test_processor_detects_duplicate_emails() -> None:
    processor = CsvProcessor()

    result = processor.process(
        FIXTURES / "duplicate_customers.csv"
    )

    assert result.records_received == 3
    assert result.records_processed == 2
    assert result.records_rejected == 0
    assert result.duplicate_records == 1



def test_processor_writes_cleaned_csv(tmp_path: Path) -> None:
    processor = CsvProcessor()

    output_file = tmp_path / "cleaned.csv"

    result = processor.process(
        FIXTURES / "duplicate_customers.csv",
        output_path=output_file,
    )

    assert output_file.exists()
    assert result.output_path == output_file


def test_processor_writes_rejected_rows_csv(tmp_path: Path) -> None:
    processor = CsvProcessor()

    output_file = tmp_path / "cleaned.csv"
    error_file = tmp_path / "rejected.csv"

    result = processor.process(
        FIXTURES / "invalid_email.csv",
        output_path=output_file,
        error_path=error_file,
    )

    assert output_file.exists()
    assert error_file.exists()

    assert result.records_received == 3
    assert result.records_processed == 2
    assert result.records_rejected == 1

    assert result.output_path == output_file
    assert result.error_path == error_file

    contents = error_file.read_text()

    assert "not-an-email" in contents