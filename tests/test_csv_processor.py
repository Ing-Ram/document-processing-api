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
