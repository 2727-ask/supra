import json
import os
from pathlib import Path

def log_plan(plan_data: dict, filename: str = "plan.json"):
    """
    Logs the plan data to a JSON file in the 'logs' directory.
    Overwrites the file if it exists.
    """
    LOGS_DIR = Path("logs")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    file_path = LOGS_DIR / filename
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(plan_data, f, indent=2, default=str)
        print(f"Plan logged to: {file_path}")
    except Exception as e:
        print(f"Failed to log plan: {e}")
