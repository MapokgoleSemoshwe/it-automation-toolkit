"""
src/file_manager.py
FileManager — organises files by type, flags duplicates/unrecognised
files, logs every action. Backend for the "File automation" requirement.
"""

import os
import shutil
import logging
from datetime import datetime

CATEGORY_MAP = {
    ".txt": "Documents", ".pdf": "Documents", ".docx": "Documents", ".csv": "Documents",
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
    ".py": "Scripts", ".sh": "Scripts", ".js": "Scripts",
    ".zip": "Archives", ".rar": "Archives", ".tar": "Archives",
    ".mp3": "Audio", ".wav": "Audio",
    ".mp4": "Video", ".mov": "Video",
}


class FileManager:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger("FileManager")
        logger.setLevel(logging.INFO)
        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)
        log_path = os.path.join(self.log_dir, "file_manager.log")
        handler = logging.FileHandler(log_path)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        return logger

    def organize(self, source: str, dry_run: bool = False) -> dict:
        if not os.path.isdir(source):
            raise NotADirectoryError(f"'{source}' is not a valid folder.")

        seen_filenames = set()
        moved, skipped, duplicates, unrecognised = 0, 0, 0, 0
        actions = []

        for entry in os.listdir(source):
            full_path = os.path.join(source, entry)
            if os.path.isdir(full_path):
                continue

            if entry in seen_filenames:
                self.logger.warning(f"Duplicate filename detected: {entry}")
                duplicates += 1
            seen_filenames.add(entry)

            _, ext = os.path.splitext(entry)
            ext = ext.lower()

            if not ext:
                unrecognised += 1
                category = "Unrecognised"
            else:
                category = CATEGORY_MAP.get(ext, "Other")

            dest_folder = os.path.join(source, category)
            dest_path = os.path.join(dest_folder, entry)

            if dry_run:
                actions.append(f"[DRY RUN] Would move '{entry}' -> '{category}/'")
                continue

            os.makedirs(dest_folder, exist_ok=True)
            try:
                shutil.move(full_path, dest_path)
                self.logger.info(f"Moved '{entry}' -> '{category}/'")
                actions.append(f"Moved '{entry}' -> '{category}/'")
                moved += 1
            except Exception as e:
                self.logger.error(f"Failed to move '{entry}': {e}")
                actions.append(f"FAILED to move '{entry}': {e}")
                skipped += 1

        summary = {
            "moved": moved, "skipped": skipped,
            "duplicates": duplicates, "unrecognised": unrecognised,
            "actions": actions,
        }
        self.logger.info(f"Summary: {summary}")
        return summary
