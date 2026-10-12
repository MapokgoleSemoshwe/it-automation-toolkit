"""
main.py
--------
IT Operations Automation Toolkit — CLI entry point.

Wires together every backend module: file organisation, log analysis,
system health checks, data validation, and reporting. This is what
gui.py calls under the hood, and it also works standalone from the
command line for anyone (e.g. a marker) without the GUI.

Usage examples:
    python main.py --organize ./messy_folder
    python main.py --analyze-log ./sample.log
    python main.py --health-check --threshold 85
    python main.py --validate-csv ./users.csv
    python main.py --full-report ./messy_folder ./sample.log ./users.csv
"""

import argparse
import sys

from src.file_manager import FileManager
from src.log_analyser import LogAnalyser
from src.system_monitor import SystemMonitor
from src.data_validator import DataValidator
from src.report_generator import ReportGenerator


def run_full_report(folder=None, logfile=None, csvfile=None, threshold=80.0):
    checks_performed = []
    problems_detected = []
    recommended_actions = []

    if folder:
        fm = FileManager()
        result = fm.organize(folder, dry_run=True)
        checks_performed.append(f"File organisation scan of '{folder}'")
        if result["duplicates"]:
            problems_detected.append(f"{result['duplicates']} duplicate filename(s) found")
            recommended_actions.append("Review and remove duplicate files")
        if result["unrecognised"]:
            problems_detected.append(f"{result['unrecognised']} file(s) with no extension")
            recommended_actions.append("Rename or classify unrecognised files")

    if logfile:
        la = LogAnalyser()
        results = la.analyze(logfile)
        checks_performed.append(f"Log analysis of '{logfile}'")
        problems_detected.extend(la.summarize(results))
        if results["severity_counts"].get("ERROR", 0) > 0:
            recommended_actions.append("Investigate repeated ERROR entries in the log")

    sm = SystemMonitor(threshold=threshold)
    health = sm.check_all()
    checks_performed.append("System health check (CPU, memory, disk)")
    for check in health:
        if check["status"] == "WARNING":
            problems_detected.append(f"{check['name']} usage at {check['value']}% (threshold {threshold}%)")
            recommended_actions.append(f"Free up {check['name'].lower()} resources")

    if csvfile:
        dv = DataValidator()
        try:
            validation = dv.validate_csv(csvfile)
            checks_performed.append(f"Data validation of '{csvfile}'")
            if validation["invalid_rows"]:
                problems_detected.append(f"{len(validation['invalid_rows'])} invalid row(s) in CSV")
                recommended_actions.append("Fix missing required fields in flagged CSV rows")
            if validation["duplicate_rows"]:
                problems_detected.append(f"{len(validation['duplicate_rows'])} duplicate row(s) in CSV")
                recommended_actions.append("Remove duplicate records from CSV")
        except (FileNotFoundError, ValueError) as e:
            problems_detected.append(str(e))

    if not problems_detected:
        problems_detected.append("No issues detected.")
    if not recommended_actions:
        recommended_actions.append("No action needed — system looks healthy.")

    rg = ReportGenerator()
    report_data = rg.build_report_data(checks_performed, problems_detected, recommended_actions)
    paths = rg.generate(report_data)
    return report_data, paths


def main():
    parser = argparse.ArgumentParser(description="IT Operations Automation Toolkit")
    parser.add_argument("--organize", metavar="FOLDER", help="Organise files in FOLDER")
    parser.add_argument("--analyze-log", metavar="LOGFILE", help="Analyse LOGFILE")
    parser.add_argument("--health-check", action="store_true", help="Run a system health check")
    parser.add_argument("--validate-csv", metavar="CSVFILE", help="Validate a CSV of records")
    parser.add_argument("--full-report", nargs="*", metavar=("FOLDER", "LOGFILE"),
                         help="Run everything and produce a full report")
    parser.add_argument("--threshold", type=float, default=80.0, help="Health check warning threshold")
    args = parser.parse_args()

    if args.organize:
        fm = FileManager()
        result = fm.organize(args.organize, dry_run=False)
        print(result)

    elif args.analyze_log:
        la = LogAnalyser()
        print(la.analyze(args.analyze_log))

    elif args.health_check:
        sm = SystemMonitor(threshold=args.threshold)
        for check in sm.check_all():
            print(check)

    elif args.validate_csv:
        dv = DataValidator()
        print(dv.validate_csv(args.validate_csv))

    elif args.full_report is not None:
        folder = args.full_report[0] if len(args.full_report) > 0 else None
        logfile = args.full_report[1] if len(args.full_report) > 1 else None
        report_data, paths = run_full_report(folder=folder, logfile=logfile, threshold=args.threshold)
        print("Report generated:")
        for p in paths:
            print(f"  - {p}")

    else:
        parser.print_help()


if __name__ == "__main__":
    sys.exit(main() or 0)
