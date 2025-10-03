from pathlib import Path
import zipfile

from ingevec_presence.models import PresenceRecord
from ingevec_presence.xlsx_writer import write_presence_workbook


def test_write_presence_workbook(tmp_path: Path):
    records = [
        PresenceRecord(date="2024-05-01", presence="87%"),
        PresenceRecord(date="2024-05-02", presence="88%"),
    ]

    output = tmp_path / "presence.xlsx"
    write_presence_workbook(records, output)

    assert output.exists()

    with zipfile.ZipFile(output, "r") as workbook:
        files = set(workbook.namelist())
        assert "[Content_Types].xml" in files
        assert "xl/worksheets/sheet1.xml" in files
        sheet_data = workbook.read("xl/worksheets/sheet1.xml").decode("utf-8")
        assert "2024-05-01" in sheet_data
        assert "87%" in sheet_data
