"""
Automated Unit Tests for Late-Event Correction Framework
CoE Review 3 Evaluation Suite
"""
import unittest
from src.delta_accumulator import LateEventCorrectionFramework
from src.baseline import BaselineAggregator
from src.config import load_rules

class TestLateEventCorrection(unittest.TestCase):
    def setUp(self):
        self.config = load_rules()
        self.framework = LateEventCorrectionFramework(self.config)
        self.baseline = BaselineAggregator()

    def test_edge_case_1_severely_delayed_lab(self):
        """Test case 1: 82-hour delayed ICU lab panel correctly attributes to Oct 1"""
        on_time_event = {
            "event_id": "LAB-001",
            "source_feed": "LABORATORY",
            "event_timestamp": "2026-10-01T08:00:00",
            "arrival_timestamp": "2026-10-01T08:30:00",
            "metric_name": "diagnostic_test_count",
            "value": 1.0
        }
        delayed_event = {
            "event_id": "LAB-002",
            "source_feed": "LABORATORY",
            "event_timestamp": "2026-10-01T22:00:00",
            "arrival_timestamp": "2026-10-05T08:00:00", # 82 hours late
            "metric_name": "diagnostic_test_count",
            "value": 1.0
        }
        self.framework.process_event(on_time_event)
        res = self.framework.process_event(delayed_event)

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(self.framework.daily_aggregates["2026-10-01"]["diagnostic_test_count"], 2.0)
        self.assertNotIn("2026-10-05", self.framework.daily_aggregates)

    def test_edge_case_2_anti_double_counting(self):
        """Test case 2: Dosage halving $350 -> $175 nets to $175, duplicates ignored"""
        initial = {
            "event_id": "BILL-100",
            "source_feed": "BILLING",
            "event_timestamp": "2026-10-01T10:00:00",
            "arrival_timestamp": "2026-10-01T10:15:00",
            "metric_name": "daily_revenue_usd",
            "value": 350.00
        }
        adjustment = {
            "event_id": "BILL-100",
            "source_feed": "BILLING",
            "event_timestamp": "2026-10-01T10:00:00",
            "arrival_timestamp": "2026-10-03T10:15:00",
            "metric_name": "daily_revenue_usd",
            "value": 175.00,
            "is_adjustment": True
        }
        duplicate = {
            "event_id": "BILL-100",
            "source_feed": "BILLING",
            "event_timestamp": "2026-10-01T10:00:00",
            "arrival_timestamp": "2026-10-03T10:20:00",
            "metric_name": "daily_revenue_usd",
            "value": 175.00,
            "retransmitted": True
        }

        self.framework.process_event(initial)
        res_adj = self.framework.process_event(adjustment)
        res_dup = self.framework.process_event(duplicate)

        # Baseline sums all three: 350 + 175 + 175 = 700 (Flawed!)
        self.baseline.ingest(initial)
        self.baseline.ingest(adjustment)
        self.baseline.ingest(duplicate)

        self.assertEqual(self.baseline.daily_metrics["2026-10-01"]["daily_revenue_usd"], 700.00)
        # Framework nets to exactly $175.00
        self.assertEqual(self.framework.daily_aggregates["2026-10-01"]["daily_revenue_usd"], 175.00)
        self.assertEqual(res_dup["status"], "IGNORED_DUPLICATE_NO_DELTA")

    def test_edge_case_3_future_clock_drift(self):
        """Test case 3: Events with future clock drift > 15 mins quarantined"""
        future_event = {
            "event_id": "PHARM-999",
            "source_feed": "PHARMACY",
            "event_timestamp": "2026-10-15T00:00:00", # 14 days in future
            "arrival_timestamp": "2026-10-01T12:00:00",
            "metric_name": "dispensation_count",
            "value": 5.0
        }
        res = self.framework.process_event(future_event)
        self.assertEqual(res["status"], "QUARANTINED")
        self.assertEqual(len(self.framework.quarantine_queue), 1)

if __name__ == "__main__":
    unittest.main()
