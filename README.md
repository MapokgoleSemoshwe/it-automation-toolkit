# IT Operations Automation Toolkit

A Python-based toolkit that automates common IT-support tasks: organising
files, analysing logs, checking system health, validating user/device
data, and generating a summary report — all from one graphical interface.

## Problem it solves

A growing organisation currently does IT-support tasks manually: staff
inspect folders, review log files, check computer health and prepare
reports by hand. This toolkit automates all of that.

## Features

1. **File automation** — sorts files into folders by type, flags duplicate
   filenames and unrecognised files, logs every action.
2. **Log analysis** — extracts dates, IP addresses and severity levels
   (ERROR/WARNING/CRITICAL) from any log file using regex, with a
   repeated-error summary.
3. **System health monitoring** — checks CPU, memory and disk usage
   against a configurable warning threshold.
4. **User/device data processing** — validates a CSV of records, flags
   missing fields and duplicates, and writes a cleaned output file.
5. **Reporting** — generates a summary report (date, checks performed,
   problems detected, recommended actions) in JSON, CSV, HTML and text.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Graphical interface (recommended for demos)
```bash
python gui.py
```
Browse for a folder/log/CSV, set a threshold, and click any action
button — or click "Run Full Report" to run everything at once.

### Command line
```bash
python main.py --organize ./some_folder
python main.py --analyze-log ./sample.log
python main.py --health-check --threshold 85
python main.py --validate-csv ./users.csv
python main.py --full-report ./some_folder ./sample.log
```

## Project structure

```
it-automation-toolkit/
├── src/
│   ├── file_manager.py       # File automation
│   ├── log_analyser.py       # Log analysis
│   ├── system_monitor.py     # System health monitoring
│   ├── data_validator.py     # CSV validation
│   ├── report_generator.py   # Report generation
│   └── api_fetcher.py        # Public API fetching (Week 4)
├── tests/
│   └── test_automation_scripts.py
├── data/                     # Sample input files
├── logs/                     # Generated log files (auto-created)
├── reports/                  # Generated reports (auto-created)
├── main.py                   # CLI entry point
├── gui.py                    # Graphical frontend
└── requirements.txt
```

## Testing

```bash
python -m unittest discover tests -v
```

## Sample input/output

Sample files are provided in `data/` — a demo log file and a demo CSV
with intentionally messy rows (a missing email, a duplicate record) to
show the validator catching real issues.

## Troubleshooting notes

See `TROUBLESHOOTING.md` for the debugging log kept during development.

## Author reflection

_(Add your own short reflection here before submission — what you
learned, what was hardest, what you'd improve.)_
