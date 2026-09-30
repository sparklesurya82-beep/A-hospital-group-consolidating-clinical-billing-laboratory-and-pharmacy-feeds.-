"""
Data models for Late-Event Correction Framework
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class IngestionEvent:
    event_id: str
    source_feed: str       # CLINICAL, BILLING, LABORATORY, PHARMACY
    event_timestamp: str   # ISO format
    arrival_timestamp: str # ISO format
    metric_name: str       # e.g., daily_revenue_usd, diagnostic_test_count, bed_day_count
    value: float
    is_adjustment: bool = False
    retransmitted: bool = False
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AuditRecord:
    audit_id: str
    timestamp: str
    event_id: str
    feed_type: str
    window_date: str
    metric_name: str
    previous_value: float
    new_value: float
    delta_applied: float
    actor_role: str
    reason_code: str
    hash: str
