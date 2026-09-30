"""
Core Late-Event Correction Engine implementing Idempotency and Bi-temporal Delta Correction
"""
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from .audit_ledger import AuditLedger

class LateEventCorrectionFramework:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.audit_ledger = AuditLedger()
        
        # State Store: window_date -> metric_name -> current_aggregate
        self.daily_aggregates: Dict[str, Dict[str, float]] = {}
        
        # Idempotent State Table: event_hash -> prior_contribution
        self.event_state: Dict[str, float] = {}

        # Quarantine Dead-Letter Queue for anomalies
        self.quarantine_queue: List[Dict[str, Any]] = []

    def compute_idempotency_key(self, event: Dict[str, Any]) -> str:
        raw_key = f"{event['source_feed']}|{event['event_id']}|{event['metric_name']}"
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def process_event(self, event: Dict[str, Any], actor_role: str = "SYSTEM_ENGINE") -> Dict[str, Any]:
        t_e = datetime.fromisoformat(event["event_timestamp"])
        t_a = datetime.fromisoformat(event["arrival_timestamp"])
        feed = event["source_feed"]
        metric = event["metric_name"]
        new_val = float(event["value"])
        window_date = t_e.date().isoformat()

        # 1. Anomaly Check: Clock Drift / Future Date Violation
        clock_drift = (t_e - t_a).total_seconds() / 60.0
        max_drift = self.config.get("anomaly_detection", {}).get("max_acceptable_clock_drift_minutes", 15)
        if clock_drift > max_drift:
            event["quarantine_reason"] = f"Clock drift violation (+{clock_drift:.1f} mins in future)"
            self.quarantine_queue.append(event)
            return {"status": "QUARANTINED", "reason": event["quarantine_reason"]}

        # 2. High-Value Billing Check (Routes to Auditor Manual Sign-off)
        threshold = self.config.get("manual_review_threshold_amount", 2500.00)
        if feed == "BILLING" and abs(new_val) >= threshold and not event.get("manual_approved", False):
            event["hold_reason"] = f"Billing adjustment >= ${threshold:.2f} requires Auditor approval"
            return {"status": "HELD_FOR_MANUAL_REVIEW", "delta_pending": new_val, "event": event}

        # 3. Anti-Double Counting: Delta Arithmetic
        idemp_key = self.compute_idempotency_key(event)
        prior_val = self.event_state.get(idemp_key, 0.0)

        # Delta calculation: Delta = C_new - C_prior
        delta = new_val - prior_val

        if window_date not in self.daily_aggregates:
            self.daily_aggregates[window_date] = {}
        if metric not in self.daily_aggregates[window_date]:
            self.daily_aggregates[window_date][metric] = 0.0

        current_agg = self.daily_aggregates[window_date][metric]

        if delta == 0.0:
            # Re-transmission or duplicate packet -> Ignored with zero impact on aggregate!
            return {"status": "IGNORED_DUPLICATE_NO_DELTA", "delta": 0.0}

        # Apply Delta to historical window
        new_agg = current_agg + delta
        self.daily_aggregates[window_date][metric] = round(new_agg, 2)
        self.event_state[idemp_key] = new_val

        # Calculate arrival latency
        delay_hours = (t_a - t_e).total_seconds() / 3600.0
        reason = f"LATE_EVENT_ARRIVED_DELAY_{delay_hours:.1f}H" if delay_hours > 0 else "ON_TIME_INGESTION"
        if prior_val > 0.0:
            reason = "RETROACTIVE_CORRECTION_DELTA"

        # Record in auditable decision trail
        self.audit_ledger.record_entry(
            event_id=event["event_id"],
            feed_type=feed,
            window_date=window_date,
            metric_name=metric,
            prev_val=current_agg,
            new_val=new_agg,
            delta=delta,
            actor_role=actor_role,
            reason=reason
        )

        return {"status": "SUCCESS", "delta": delta, "new_aggregate": new_agg}

    def manual_override_approve(self, event: Dict[str, Any], auditor_id: str, justification: str) -> Dict[str, Any]:
        event["manual_approved"] = True
        return self.process_event(event, actor_role=f"BILLING_AUDITOR:{auditor_id}:{justification}")
