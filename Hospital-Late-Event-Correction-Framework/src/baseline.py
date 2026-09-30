"""
Baseline Naive Aggregator demonstrating double-counting flaws
"""
from datetime import datetime
from typing import Dict, Any

class BaselineAggregator:
    def __init__(self):
        self.daily_metrics: Dict[str, Dict[str, float]] = {}
        self.double_count_events = 0

    def ingest(self, event: Dict[str, Any]):
        t_event = datetime.fromisoformat(event["event_timestamp"]).date().isoformat()
        metric = event["metric_name"]
        val = float(event["value"])

        if t_event not in self.daily_metrics:
            self.daily_metrics[t_event] = {}
        if metric not in self.daily_metrics[t_event]:
            self.daily_metrics[t_event][metric] = 0.0

        if event.get("retransmitted") or event.get("is_adjustment"):
            self.double_count_events += 1

        self.daily_metrics[t_event][metric] += val
