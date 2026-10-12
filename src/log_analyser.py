"""
src/log_analyser.py
LogAnalyser — extracts dates, IPs and severity levels from a log file
using regex. Backend for the "Log analysis" requirement.
"""

import re
from collections import Counter


class LogAnalyser:
    DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b")
    IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    SEVERITY_PATTERN = re.compile(r"\b(ERROR|WARNING|CRITICAL|FAILURE)\b", re.IGNORECASE)

    def analyze(self, filepath: str) -> dict:
        dates_found = []
        ips_found = []
        severity_counter = Counter()
        flagged_lines = []

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_number, line in enumerate(f, start=1):
                dates_found += self.DATE_PATTERN.findall(line)
                ips_found += self.IP_PATTERN.findall(line)

                match = self.SEVERITY_PATTERN.search(line)
                if match:
                    level = match.group(1).upper()
                    severity_counter[level] += 1
                    flagged_lines.append({"line": line_number, "level": level, "text": line.strip()})

        return {
            "total_dates": len(dates_found),
            "unique_dates": sorted(set(dates_found)),
            "unique_ips": sorted(set(ips_found)),
            "severity_counts": dict(severity_counter),
            "flagged_lines": flagged_lines,
        }

    def summarize(self, results: dict) -> list:
        """Returns a list of short human-readable strings for the report."""
        lines = [f"{len(results['unique_ips'])} unique IP address(es) found."]
        for level, count in results["severity_counts"].items():
            lines.append(f"{count} {level} entr{'y' if count == 1 else 'ies'} found.")
        return lines
