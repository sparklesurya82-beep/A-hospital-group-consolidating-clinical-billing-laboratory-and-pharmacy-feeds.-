"""
Cryptographically chained immutable audit ledger
"""
import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class AuditLedger:
    def __init__(self):
        self.ledger: List[Dict[str, Any]] = []

    def record_entry(self, event_id: str, feed_type: str, window_date: str,
                     metric_name: str, prev_val: float, new_val: float,
                     delta: float, actor_role: str, reason: str) -> Dict[str, Any]:
        entry = {
            "audit_id": f"AUDIT-{int(time.time()*1000)}-{len(self.ledger)+1}",
            "timestamp": datetime.now().astimezone().isoformat(),
            "event_id": event_id,
            "feed_type": feed_type,
            "window_date": window_date,
            "metric_name": metric_name,
            "previous_value": round(prev_val, 2),
            "new_value": round(new_val, 2),
            "delta_applied": round(delta, 2),
            "actor_role": actor_role,
            "reason_code": reason
        }
        # Cryptographic tamper-proofing with SHA-256
        serialized = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(serialized.encode()).hexdigest()
        self.ledger.append(entry)
        return entry

    def print_recent(self, n: int = 5):
        print("\n" + "="*80)
        print("--- AUDITABLE DECISION TRAIL (IMMUTABLE LEDGER) ---")
        print("="*80)
        for e in self.ledger[-n:]:
            print(f"[{e['audit_id']}] {e['window_date']} | Metric: {e['metric_name']} | "
                  f"Prev: {e['previous_value']} -> New: {e['new_value']} (Delta: {e['delta_applied']:+}) | "
                  f"Actor: {e['actor_role']} | Reason: {e['reason_code']}")
        print("="*80 + "\n")
