"""
gui.py
-------
IT Operations Automation Toolkit — Graphical Frontend

This is what you run for your presentation instead of executing each
script from the command line. It gives you:
- Buttons to browse for a folder (for file organising) or files
  (for log analysis / CSV validation).
- A threshold input for the system health check.
- One button per module, plus a "Run Full Report" button that runs
  everything and generates the final report.
- An output panel showing results live, so the audience can see what's
  happening without you switching to a terminal.

Built with Tkinter because it ships with Python — no extra install
needed, which matters on demo day.

Usage:
    python gui.py
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from src.file_manager import FileManager
from src.log_analyser import LogAnalyser
from src.system_monitor import SystemMonitor
from src.data_validator import DataValidator
from src.report_generator import ReportGenerator
from main import run_full_report


class ToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("IT Operations Automation Toolkit")
        self.root.geometry("760x620")

        # Variables that hold whatever the user picks via the browse buttons
        self.folder_path = tk.StringVar()
        self.log_path = tk.StringVar()
        self.csv_path = tk.StringVar()
        self.threshold = tk.StringVar(value="80")

        self._build_layout()

    # ---------- UI construction ----------

    def _build_layout(self):
        pad = {"padx": 10, "pady": 6}

        title = tk.Label(self.root, text="IT Operations Automation Toolkit",
                          font=("Segoe UI", 16, "bold"))
        title.pack(pady=(15, 5))

        subtitle = tk.Label(self.root, text="Select your inputs below, then run a module or the full report.",
                             font=("Segoe UI", 10))
        subtitle.pack(pady=(0, 10))

        # --- Input section ---
        input_frame = tk.LabelFrame(self.root, text="Inputs", padx=10, pady=10)
        input_frame.pack(fill="x", **pad)

        self._make_picker_row(input_frame, "Folder to organise:", self.folder_path, self._browse_folder)
        self._make_picker_row(input_frame, "Log file to analyse:", self.log_path, self._browse_log)
        self._make_picker_row(input_frame, "CSV file to validate:", self.csv_path, self._browse_csv)

        threshold_row = tk.Frame(input_frame)
        threshold_row.pack(fill="x", pady=4)
        tk.Label(threshold_row, text="Health check threshold (%):", width=22, anchor="w").pack(side="left")
        tk.Entry(threshold_row, textvariable=self.threshold, width=10).pack(side="left")

        # --- Actions section ---
        action_frame = tk.LabelFrame(self.root, text="Actions", padx=10, pady=10)
        action_frame.pack(fill="x", **pad)

        buttons = [
            ("Organise Files", self.run_organize),
            ("Analyse Log", self.run_log_analysis),
            ("Check System Health", self.run_health_check),
            ("Validate CSV Data", self.run_csv_validation),
        ]
        btn_row = tk.Frame(action_frame)
        btn_row.pack(fill="x")
        for text, command in buttons:
            tk.Button(btn_row, text=text, command=command, width=20).pack(side="left", padx=4, pady=4)

        tk.Button(action_frame, text="Run Full Report (all modules)", command=self.run_full,
                  bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold")).pack(fill="x", pady=(10, 0))

        # --- Output section ---
        output_frame = tk.LabelFrame(self.root, text="Output", padx=10, pady=10)
        output_frame.pack(fill="both", expand=True, **pad)

        self.output_box = scrolledtext.ScrolledText(output_frame, wrap="word", font=("Consolas", 10))
        self.output_box.pack(fill="both", expand=True)

        self.status_bar = tk.Label(self.root, text="Ready.", anchor="w", relief="sunken")
        self.status_bar.pack(fill="x", side="bottom")

    def _make_picker_row(self, parent, label_text, variable, browse_command):
        row = tk.Frame(parent)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label_text, width=22, anchor="w").pack(side="left")
        tk.Entry(row, textvariable=variable, width=55).pack(side="left", padx=4)
        tk.Button(row, text="Browse...", command=browse_command).pack(side="left")

    # ---------- Browse handlers ----------

    def _browse_folder(self):
        path = filedialog.askdirectory(title="Select folder to organise")
        if path:
            self.folder_path.set(path)

    def _browse_log(self):
        path = filedialog.askopenfilename(title="Select log file",
                                           filetypes=[("Log/Text files", "*.log *.txt"), ("All files", "*.*")])
        if path:
            self.log_path.set(path)

    def _browse_csv(self):
        path = filedialog.askopenfilename(title="Select CSV file",
                                           filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            self.csv_path.set(path)

    # ---------- Output helpers ----------

    def log(self, message: str):
        self.output_box.insert(tk.END, message + "\n")
        self.output_box.see(tk.END)
        self.root.update_idletasks()

    def set_status(self, message: str):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def _get_threshold(self):
        try:
            return float(self.threshold.get())
        except ValueError:
            messagebox.showerror("Invalid threshold", "Threshold must be a number, e.g. 80")
            return None

    # ---------- Action handlers ----------

    def run_organize(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Missing input", "Please choose a folder first.")
            return
        self.set_status("Organising files...")
        try:
            fm = FileManager()
            result = fm.organize(folder, dry_run=False)
            self.log(f"\n--- File Organisation: {folder} ---")
            for action in result["actions"]:
                self.log(action)
            self.log(f"Summary: moved={result['moved']}, duplicates={result['duplicates']}, "
                      f"unrecognised={result['unrecognised']}, skipped={result['skipped']}")
            self.set_status("File organisation complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error during file organisation.")

    def run_log_analysis(self):
        logfile = self.log_path.get()
        if not logfile:
            messagebox.showwarning("Missing input", "Please choose a log file first.")
            return
        self.set_status("Analysing log...")
        try:
            la = LogAnalyser()
            results = la.analyze(logfile)
            self.log(f"\n--- Log Analysis: {logfile} ---")
            self.log(f"Unique IPs: {results['unique_ips']}")
            self.log(f"Unique dates: {results['unique_dates']}")
            self.log(f"Severity counts: {results['severity_counts']}")
            for item in la.summarize(results):
                self.log(f"  - {item}")
            self.set_status("Log analysis complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error during log analysis.")

    def run_health_check(self):
        threshold = self._get_threshold()
        if threshold is None:
            return
        self.set_status("Checking system health...")
        try:
            sm = SystemMonitor(threshold=threshold)
            self.log(f"\n--- System Health Check (threshold {threshold}%) ---")
            for check in sm.check_all():
                self.log(f"{check['name']}: {check['value']}%  [{check['status']}]")
            self.set_status("Health check complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error during health check.")

    def run_csv_validation(self):
        csvfile = self.csv_path.get()
        if not csvfile:
            messagebox.showwarning("Missing input", "Please choose a CSV file first.")
            return
        self.set_status("Validating CSV...")
        try:
            dv = DataValidator()
            results = dv.validate_csv(csvfile)
            self.log(f"\n--- CSV Validation: {csvfile} ---")
            self.log(f"Valid rows: {len(results['valid_rows'])}")
            self.log(f"Invalid rows: {len(results['invalid_rows'])}")
            self.log(f"Duplicate rows: {len(results['duplicate_rows'])}")

            output_path = os.path.join(os.path.dirname(csvfile) or ".", "cleaned_output.csv")
            dv.write_cleaned_csv(results["valid_rows"], output_path)
            self.log(f"Cleaned file written to: {output_path}")
            self.set_status("CSV validation complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error during CSV validation.")

    def run_full(self):
        threshold = self._get_threshold()
        if threshold is None:
            return
        self.set_status("Running full report across all modules...")
        try:
            report_data, paths = run_full_report(
                folder=self.folder_path.get() or None,
                logfile=self.log_path.get() or None,
                csvfile=self.csv_path.get() or None,
                threshold=threshold,
            )
            self.log("\n=== FULL REPORT ===")
            self.log(f"Date: {report_data['date']}")
            self.log("Checks performed:")
            for c in report_data["checks_performed"]:
                self.log(f"  - {c}")
            self.log("Problems detected:")
            for p in report_data["problems_detected"]:
                self.log(f"  - {p}")
            self.log("Recommended actions:")
            for a in report_data["recommended_actions"]:
                self.log(f"  - {a}")
            self.log("\nReport files saved:")
            for p in paths:
                self.log(f"  - {p}")
            self.set_status("Full report complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error while generating full report.")


def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        style.theme_use("clam")
    except Exception:
        pass
    app = ToolkitGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
