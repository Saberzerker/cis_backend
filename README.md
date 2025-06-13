# CIS Backend Automation

## Directory Structure

- `data/input/` — Place raw PDFs here for parsing.
- `data/output/text/`, `json/`, `csv/`, `validation/` — Outputs from parser.
- `pdf_accurate/` — PDFs parsed with no LLM-reported discrepancies.
- `pdf_discrepancy/` — PDFs with detected discrepancies.
- `pdf_reports/` — Validation/discrepancy JSON reports.
- `pdf_versions/` — All downloaded CIS PDFs (auto-update).
- `reports/` — GRC PDF and stats output.
- `logs/` — Logging.

## Usage

1. Parse & Validate all PDFs:
   ```bash
   python main.py
   ```

2. Generate GRC Report:
   ```bash
   python generate_report.py --checklist <your_checklist.json> --device <DeviceName> --host <HostName>
   ```

3. Auto-update CIS PDFs:
   ```bash
   python auto_update.py
   ```

## Requirements

```bash
pip install -r requirements.txt
```
