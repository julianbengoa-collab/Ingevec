# INGVEC presence automation

This repository contains a small automation that downloads the "Presencia Bursátil" table
from the [Bolsa de Santiago](https://www.bolsadesantiago.com/presencia_bursatil) website, extracts
the presence associated with the INGVEC ticker and stores the information in an Excel workbook.

The solution only relies on the Python standard library so it can run in environments without
internet access to install additional dependencies.

## Usage

1. Create a Python virtual environment (optional but recommended) and activate it.
2. Execute the script:

   ```bash
   python -m ingevec_presence.scripts.fetch_presence
   ```

   This command will download the latest page, parse the table and export an Excel file at
   `data/presencia_ingvec.xlsx`. Historical values are kept inside `data/presence_history.json`.

3. Verify the generated Excel file to confirm the recorded presence value.

### Scheduling a daily execution at 09:00

To automate the process every day at 9 AM (America/Santiago), add the following cron entry:

```cron
0 9 * * * /usr/bin/python -m ingevec_presence.scripts.fetch_presence >> /path/to/repo/data/cron.log 2>&1
```

Adjust the Python interpreter path and repository location as needed. Cron will run the script daily
and append the log output to `data/cron.log`.

## Development

Unit tests cover the HTML parsing logic and the Excel export helper. Run them with:

```bash
pytest
```
