"""
src/data_validator.py
DataValidator — reads user/device records from a CSV, validates
required fields, flags invalid or duplicate records, and writes a
cleaned output file. Backend for "User or device data processing".
"""

import csv
import os


class DataValidator:
    def __init__(self, required_fields=None):
        # Sensible default for a "user/device record" CSV — override
        # with whatever columns your actual data uses.
        self.required_fields = required_fields or ["name", "email"]

    def validate_csv(self, filepath: str) -> dict:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        valid_rows = []
        invalid_rows = []
        seen = set()
        duplicate_rows = []

        with open(filepath, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            missing_columns = [field for field in self.required_fields if field not in (reader.fieldnames or [])]
            if missing_columns:
                raise ValueError(f"CSV is missing required column(s): {missing_columns}")

            row_number = 1
            for row_number, row in enumerate(reader, start=2):  # row 1 is the header
                missing = [field for field in self.required_fields if not row.get(field, "").strip()]
                if missing:
                    invalid_rows.append({"row": row_number, "data": row, "reason": f"Missing: {missing}"})
                    continue

                # Build a key from the required fields to detect duplicates
                key = tuple(row[field].strip().lower() for field in self.required_fields)
                if key in seen:
                    duplicate_rows.append({"row": row_number, "data": row})
                    continue
                seen.add(key)
                valid_rows.append(row)

        return {
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "duplicate_rows": duplicate_rows,
            "total_processed": row_number - 1,
        }

    def write_cleaned_csv(self, valid_rows: list, output_path: str) -> str:
        if not valid_rows:
            # Still create an empty file with headers so downstream steps don't break
            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.required_fields)
                writer.writeheader()
            return output_path

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(valid_rows[0].keys()))
            writer.writeheader()
            writer.writerows(valid_rows)
        return output_path
