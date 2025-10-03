from ingevec_presence.html_table_parser import extract_tables
from ingevec_presence.presence_pipeline import extract_presence_value


def test_extract_presence_from_simple_table():
    html = """
    <html>
      <body>
        <table>
          <tr><th>Ticker</th><th>Presencia</th></tr>
          <tr><td>AAA</td><td>10%</td></tr>
          <tr><td>INGVEC</td><td>87%</td></tr>
        </table>
      </body>
    </html>
    """
    assert extract_presence_value(html) == "87%"


def test_extract_presence_with_missing_header_uses_neighbor():
    html = """
    <table>
      <tr><th>Acción</th><th>Nombre</th><th>Valor</th></tr>
      <tr><td>INGVEC</td><td>Ingevec</td><td>92%</td></tr>
    </table>
    """
    assert extract_presence_value(html) == "92%"


def test_extract_tables_ignores_empty_rows():
    html = """
    <table>
      <tr><th>Col1</th><th>Col2</th></tr>
      <tr><td>Value 1</td><td>Value 2</td></tr>
      <tr><td></td><td></td></tr>
    </table>
    """
    tables = extract_tables(html)
    assert len(tables) == 1
    assert tables[0].rows == [["Col1", "Col2"], ["Value 1", "Value 2"]]
