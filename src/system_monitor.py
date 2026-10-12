"""
src/system_monitor.py
SystemMonitor — checks CPU, memory and disk usage against a warning
threshold. Backend for the "System health monitoring" requirement.
"""

import shutil

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class SystemMonitor:
    def __init__(self, threshold: float = 80.0):
        self.threshold = threshold

    def check_cpu(self):
        if not PSUTIL_AVAILABLE:
            return {"name": "CPU", "value": None, "status": "N/A — psutil not installed"}
        try:
            usage = psutil.cpu_percent(interval=1)
            status = "WARNING" if usage >= self.threshold else "OK"
            return {"name": "CPU", "value": usage, "status": status}
        except Exception as e:
            return {"name": "CPU", "value": None, "status": f"Error: {e}"}

    def check_memory(self):
        if not PSUTIL_AVAILABLE:
            return {"name": "Memory", "value": None, "status": "N/A — psutil not installed"}
        try:
            mem = psutil.virtual_memory()
            status = "WARNING" if mem.percent >= self.threshold else "OK"
            return {"name": "Memory", "value": mem.percent, "status": status}
        except Exception as e:
            return {"name": "Memory", "value": None, "status": f"Error: {e}"}

    def check_disk(self, path: str = "/"):
        try:
            total, used, free = shutil.disk_usage(path)
            percent_used = round((used / total) * 100, 1)
            status = "WARNING" if percent_used >= self.threshold else "OK"
            return {"name": "Disk", "value": percent_used, "status": status}
        except Exception as e:
            return {"name": "Disk", "value": None, "status": f"Error: {e}"}

    def check_all(self, disk_path: str = "/") -> list:
        return [self.check_cpu(), self.check_memory(), self.check_disk(disk_path)]
