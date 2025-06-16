# CIS Backend Automation

## Directory Structure

- `data/input/` — Raw PDFs are downloaded here (`auto_update.py`).
- `output/text/`, `output/validated/json/`, `output/validated/csv/`, `output/discrepancy/json/`, `output/discrepancy/csv/`, `output/validated/reports/`, `output/discrepancy/reports/` — Outputs from the parser and validation pipeline.
- `logs/` — Logging.
- `pdf_accurate/` and `pdf_discrepancy/` — Legacy outputs (may be deprecated in new pipeline).
- `pdf_reports/` — Legacy/extra reports.
- `pdf_versions/` — All downloaded CIS PDFs (auto-update).
- `reports/` — GRC PDF and stats output.

## Usage

### 1. **Run the Pipeline (Auto-update and Parsing):**

```bash
python pipeline.py
```
- This will:
  - Check for new CIS Benchmark versions and auto-download if there is an update.
  - Parse all new PDFs (or all PDFs in the latest version folder).
  - Validate and export sorted JSON and CSV files.

### 2. **Schedule Automated Runs:**

To run the pipeline every 6 hours, use:

```bash
python scheduler.py
```

> The scheduler will keep running in the background and trigger the pipeline as per the interval.

### 3. **Generate GRC Report:**

```bash
python generate_report.py --checklist <your_checklist.json> --device <DeviceName> --host <HostName>
```

### 4. **Manual Auto-update:**

If you want to only check/download the latest PDFs:

```bash
python auto_update.py
```

## Requirements

```bash
pip install -r requirements.txt
```

## Main Scripts

- `auto_update.py`  — Scrapes CIS site and downloads new versioned PDFs.
- `main.py`         — Parses and validates PDFs (used internally by pipeline).
- `pipeline.py`     — Runs auto-update, then parsing/validation if new versions are found.
- `scheduler.py`    — Runs `pipeline.py` every 6 hours.
- `generate_report.py` — GRC and stats reporting.

---

## Output Locations

- **Validated:**  
  - `output/validated/json/` — Validated JSON records, sorted by control ID.
  - `output/validated/csv/`  — Validated CSV records, sorted by control ID.
  - `output/validated/reports/` — Detailed validation JSON reports.

- **Discrepancy:**  
  - `output/discrepancy/json/` — Discrepancy JSON records.
  - `output/discrepancy/csv/`  — Discrepancy CSV records.
  - `output/discrepancy/reports/` — Discrepancy validation reports.

- **Logs:**  
  - `logs/` — Pipeline and update logs.

---

## Scheduling/Automation

- To automate, run `scheduler.py` as a background process (e.g., with `nohup`, `tmux`, or as a system service).

---

## Notes

- All parsing, validation, and reporting are parallelized for speed.
- Control records in all outputs are sorted by their natural numeric ID (e.g., 1.1.2 before 1.1.10).
- The pipeline only re-runs parsing if an update is detected by `auto_update.py`.
