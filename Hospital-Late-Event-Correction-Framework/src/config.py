"""
Configuration loader for the rules engine
"""
import json
import os
from typing import Dict, Any

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "rules_config.json"
)

def load_rules(path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "rules_engine_version": "2.1.0",
        "system_grace_periods_hours": {
            "CLINICAL": 72,
            "BILLING": 168,
            "LABORATORY": 48,
            "PHARMACY": 24
        },
        "manual_review_threshold_amount": 2500.00,
        "anomaly_detection": {
            "max_acceptable_clock_drift_minutes": 15,
            "drop_future_dated_events": True
        }
    }
