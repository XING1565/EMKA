from io import BytesIO

from openpyxl import Workbook

from backend.app.ingestion.table_parser import parse_table_file


def test_csv_parser_outputs_summary_columns_rows_and_range():
    metadata = {}

    content = parse_table_file("risk.csv", b"date,risk,owner\n2026-07-22,delay,Alice\n", metadata)

    assert "Table summary (csv): 1 data rows" in content
    assert "row 2: date=2026-07-22; risk=delay; owner=Alice" in content
    assert metadata["table_columns"] == ["date", "risk", "owner"]
    assert metadata["row_count"] == 1
    assert metadata["row_ranges"] == ["2-2"]


def test_xlsx_parser_outputs_sheet_columns_rows_and_range():
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Q1"
    sheet.append(["date", "risk", "owner"])
    sheet.append(["2026-07-22", "delay", "Alice"])
    buffer = BytesIO()
    workbook.save(buffer)
    metadata = {}

    content = parse_table_file("risk.xlsx", buffer.getvalue(), metadata)

    assert "Table summary (Q1): 1 data rows" in content
    assert "row 2: date=2026-07-22; risk=delay; owner=Alice" in content
    assert metadata["sheet_names"] == ["Q1"]
    assert metadata["table_columns"] == ["date", "risk", "owner"]
    assert metadata["row_count"] == 1
    assert metadata["row_ranges"] == ["2-2"]
