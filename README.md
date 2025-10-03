# INGVEC presence automation

This repository contains a small automation that downloads the "Presencia Bursátil" table
from the [Bolsa de Santiago](https://www.bolsadesantiago.com/presencia_bursatil) website, extracts
the presence associated with the INGVEC ticker and stores the information in an Excel workbook.

The solution only relies on the Python standard library so it can run in environments without
internet access to install additional dependencies.

## Usage

1. Create a Python virtual environment (optional but recommended) and activate it.
2. Execute the helper script to download the latest information:

   ```bash
   ./scripts/run_fetch_presence.sh
   ```

   This command will download the latest page, parse the table and export an Excel file at
   `data/presencia_ingvec.xlsx`. Historical values are kept inside `data/presence_history.json`.

   If you prefer to call the Python module directly (for example to pass extra arguments), run:

   ```bash
   python -m ingevec_presence.scripts.fetch_presence
   ```

3. Verify the generated Excel file to confirm the recorded presence value.

> **Note**
> The automation no longer configures a daily scheduler by default. Run the helper script whenever
> you need to refresh the presence information or wire it into your own scheduling solution.

## Development

Unit tests cover the HTML parsing logic and the Excel export helper. Run them with:

```bash
pytest
```
