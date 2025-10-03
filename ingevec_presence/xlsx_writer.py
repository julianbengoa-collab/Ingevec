"""Write presence history into a minimal XLSX file without third-party libraries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
from xml.sax.saxutils import escape
import zipfile

from .models import PresenceRecord


@dataclass
class WorksheetRow:
    row_index: int
    values: List[str]

    def to_xml(self) -> str:
        cells = []
        for column_index, value in enumerate(self.values):
            cell_ref = _excel_cell_reference(row_index=self.row_index, column_index=column_index)
            cell_xml = (
                f'<c r="{cell_ref}" t="inlineStr">'
                f"<is><t>{escape(value)}</t></is>"
                "</c>"
            )
            cells.append(cell_xml)
        joined_cells = "".join(cells)
        return f"<row r=\"{self.row_index}\">{joined_cells}</row>"


def _excel_cell_reference(*, row_index: int, column_index: int) -> str:
    """Translate zero-based indexes into an Excel cell reference."""

    column = ""
    column_number = column_index + 1
    while column_number:
        column_number, remainder = divmod(column_number - 1, 26)
        column = chr(ord("A") + remainder) + column
    return f"{column}{row_index}"


CONTENT_TYPES_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'>
  <Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/>
  <Default Extension='xml' ContentType='application/xml'/>
  <Override PartName='/xl/workbook.xml' ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml'/>
  <Override PartName='/xl/worksheets/sheet1.xml' ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml'/>
  <Override PartName='/xl/styles.xml' ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml'/>
</Types>
"""

RELS_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>
  <Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument' Target='xl/workbook.xml'/>
</Relationships>
"""

WORKBOOK_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<workbook xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main' xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships'>
  <sheets>
    <sheet name='Presencia' sheetId='1' r:id='rId1'/>
  </sheets>
</workbook>
"""

WORKBOOK_RELS_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>
  <Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet' Target='worksheets/sheet1.xml'/>
  <Relationship Id='rId2' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles' Target='styles.xml'/>
</Relationships>
"""

STYLES_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<styleSheet xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'>
  <fonts count='1'>
    <font>
      <sz val='11'/>
      <color theme='1'/>
      <name val='Calibri'/>
      <family val='2'/>
    </font>
  </fonts>
  <fills count='2'>
    <fill>
      <patternFill patternType='none'/>
    </fill>
    <fill>
      <patternFill patternType='gray125'/>
    </fill>
  </fills>
  <borders count='1'>
    <border>
      <left/>
      <right/>
      <top/>
      <bottom/>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count='1'>
    <xf numFmtId='0' fontId='0' fillId='0' borderId='0'/>
  </cellStyleXfs>
  <cellXfs count='1'>
    <xf numFmtId='0' fontId='0' fillId='0' borderId='0' xfId='0'/>
  </cellXfs>
  <cellStyles count='1'>
    <cellStyle name='Normal' xfId='0' builtinId='0'/>
  </cellStyles>
</styleSheet>
"""


def _build_sheet_xml(records: Iterable[PresenceRecord]) -> str:
    rows: List[WorksheetRow] = []
    rows.append(WorksheetRow(row_index=1, values=["Fecha", "Presencia"]))
    for index, record in enumerate(records, start=2):
        rows.append(WorksheetRow(row_index=index, values=[record.date, record.presence]))
    rows_xml = "".join(row.to_xml() for row in rows)
    return (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>"
        "<worksheet xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'>"
        f"<sheetData>{rows_xml}</sheetData>"
        "</worksheet>"
    )


def write_presence_workbook(records: Iterable[PresenceRecord], path: Path) -> None:
    """Persist the provided records into an XLSX workbook."""

    path.parent.mkdir(parents=True, exist_ok=True)
    records_list = list(records)
    sheet_xml = _build_sheet_xml(records_list)

    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        workbook.writestr("_rels/.rels", RELS_XML)
        workbook.writestr("xl/workbook.xml", WORKBOOK_XML)
        workbook.writestr("xl/_rels/workbook.xml.rels", WORKBOOK_RELS_XML)
        workbook.writestr("xl/styles.xml", STYLES_XML)
        workbook.writestr("xl/worksheets/sheet1.xml", sheet_xml)
