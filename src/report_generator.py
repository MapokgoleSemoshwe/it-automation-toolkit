"""
report_generator.py
---------------------
Week 4, Monday: "Convert system data into a structured report"

What it does:
Takes raw data (a dict, or results from other scripts like the log
analyzer / health checker) and writes it out as a structured report in
whichever format you need: CSV, JSON, HTML, or plain text.

This is the "Reporting" requirement in the capstone brief — every
other module (file automation, log analysis, health checks, data
validation) can feed its results into this one class to produce the
final report.

Usage as a standalone demo:
    python report_generator.py
"""

import json
import csv
import os
from datetime import datetime


class ReportGenerator:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def build_report_data(self, checks_performed: list, problems_detected: list, recommended_actions: list) -> dict:
        """
        Assembles the report skeleton the capstone brief asks for:
        date, checks performed, problems detected, recommended actions.
        """
        return {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "checks_performed": checks_performed,
            "problems_detected": problems_detected,
            "recommended_actions": recommended_actions,
        }

    def save_as_json(self, data: dict, filename="report.json") -> str:
        path = os.path.join(self.output_dir, filename)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return path

    def save_as_csv(self, data: dict, filename="report.csv") -> str:
        path = os.path.join(self.output_dir, filename)
        # Flatten the dict into simple key,value rows since CSV is
        # naturally tabular, not nested like JSON.
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Field", "Value"])
            for key, value in data.items():
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value)
                writer.writerow([key, value])
        return path

    def save_as_text(self, data: dict, filename="report.txt") -> str:
        path = os.path.join(self.output_dir, filename)
        with open(path, "w") as f:
            f.write("=" * 50 + "\n")
            f.write("IT AUTOMATION TOOLKIT — SUMMARY REPORT\n")
            f.write("=" * 50 + "\n\n")
            for key, value in data.items():
                f.write(f"{key.replace('_', ' ').title()}:\n")
                if isinstance(value, list):
                    for item in value:
                        f.write(f"  - {item}\n")
                else:
                    f.write(f"  {value}\n")
                f.write("\n")
        return path

    def save_as_html(self, data: dict, filename="report.html") -> str:
        path = os.path.join(self.output_dir, filename)
        rows = ""
        for key, value in data.items():
            if isinstance(value, list):
                value = "<br>".join(str(v) for v in value)
            rows += f"<tr><td><b>{key.replace('_', ' ').title()}</b></td><td>{value}</td></tr>\n"

        html = f"""<!DOCTYPE html>
<html>
<head><title>IT Automation Report</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
</style>
</head>
<body>
<h1>IT Automation Toolkit — Summary Report</h1>
<table>
{rows}
</table>
</body>
</html>"""
        with open(path, "w") as f:
            f.write(html)
        return path

    def generate(self, data: dict, formats=("json", "csv", "html", "text")) -> list:
        """Generate the report in one or more formats at once."""
        saved_paths = []
        format_map = {
            "json": self.save_as_json,
            "csv": self.save_as_csv,
            "html": self.save_as_html,
            "text": self.save_as_text,
        }
        for fmt in formats:
            if fmt in format_map:
                saved_paths.append(format_map[fmt](data))
        return saved_paths


if __name__ == "__main__":
    generator = ReportGenerator()
    report_data = generator.build_report_data(
        checks_performed=["File organisation", "Log analysis", "System health check"],
        problems_detected=["2 duplicate files found", "3 ERROR entries in app.log"],
        recommended_actions=["Review duplicates in Documents folder", "Investigate repeated login failures"],
    )
    paths = generator.generate(report_data)
    print("Reports generated:")
    for p in paths:
        print(f"  - {p}")
