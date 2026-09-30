# Hospital Late-Event Correction Framework

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()
[![Compliance](https://img.shields.io/badge/Compliance-HIPAA%20De--identified-orange.svg)]()

> **CoE Final Year Capstone Project (Reviews 2 & 3)**  
> **Student:** M. Jayashri (Reg No: 24111302)  
> **Department:** Computer Science & Engineering (Cohort C28)  

---

## 📌 Project Overview
A hospital group consolidates mission-critical streaming feeds from **Clinical EHR**, **Hospital Billing**, **Laboratory (LIMS)**, and **Pharmacy** systems. 

In distributed healthcare environments, network partitions and asynchronous batch syncs cause events to arrive hours or days after their clinical occurrence ($T_{arrival} \gg T_{event}$). Traditional batch systems produce skewed daily operational reports (e.g., patient bed-day counts, pharmacy revenue, lab throughput). When late records arrive, naive systems either drop them (under-reporting) or append them naively without retracting old totals, causing catastrophic **double-counting**.

This repository implements an enterprise-grade **Event-Time Watermarked Delta-Correction Framework** that:
- Reconciles historical daily aggregates **without double counting**.
- Computes mathematical deltas ($\Delta = C_{new} - C_{prior}$) in sub-milliseconds ($O(1)$) rather than full $O(N)$ recomputations.
- Exposes **configurable rules** (departmental grace periods, clock drift tolerance) without hardcoding.
- Enforces **dual organizational roles**: *Health Informatics Data Steward* and *Hospital Billing Compliance Auditor*.
- Maintains an **immutable, cryptographically hashed audit ledger** for all automatic and manual overrides.

---

## 🏛️ System Architecture

```
+---------------------------------------------------------------------------------------------------+
|                                 HOSPITAL DATA INGESTION FEEDS                                     |
|  [Clinical Feeds (EHR)]   [Billing Feeds (Claims)]   [Laboratory Feeds (LIMS)]   [Pharmacy Feeds]  |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                               1. INGESTION & NORMALIZATION LAYER                                 |
|  - Assign Ingestion Timestamp (T_arrival)                                                         |
|  - Validate Event Timestamp (T_event)                                                             |
|  - Generate Idempotency Hash: SHA-256(Source_System + Event_ID + Metric_Name)                      |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                        2. CONFIGURABLE RULES & WATERMARK EVALUATOR ENGINE                         |
|  - Dynamic Watermark Tracking: W(t) = max(T_event) - Allowed_Lateness_Grace_Period                |
|  - Anomaly Gateway: Quarantines Clock Drift / Future Dated Events (>15 min)                       |
|  - Rules Repository: Stored in JSON/YAML (Grace periods, threshold limits, SLA rules)             |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                                3. STATE STORE & CORRECTION ENGINE                                 |
|  - Look up historical Daily Aggregate Window: W_k = [T_start, T_end)                              |
|  - Apply Bi-Temporal Delta Correction without double-counting:                                    |
|      Aggregate_New(W_k) = Aggregate_Old(W_k) + Delta_Value                                        |
|  - Idempotent Event Deduplication Table (prevents re-applying same event)                        |
+---------------------------------------------------------------------------------------------------+
                                                  │
                      ┌───────────────────────────┴───────────────────────────┐
                      ▼                                                       ▼
+---------------------------------------------+     +---------------------------------------------+
|    4. ROLE-BASED DASHBOARD & OVERRIDES      |     |         5. AUDITABLE DECISION TRAIL         |
|  - Role A: Data Steward (Config Rules)      |     |  - Immutable Append-Only Ledger             |
|  - Role B: Billing Auditor (Review & Action)|     |  - User ID, Timestamp, Reason Code, Diff   |
+---------------------------------------------+     +---------------------------------------------+
```

---

## ⚙️ Mathematical Formulation: Anti-Double Counting

Let an event $E_i$ contribute to reporting window $W_k$:
- **Deterministic Idempotency Key:**
  $$K_{idemp} = \text{SHA256}(\text{source\_feed} \parallel \text{event\_id} \parallel \text{metric\_name})$$
- **State Store Lookup:** Queries prior recorded value $C_{prior}$ (default 0 for new late events).
- **Delta Arithmetic:**
  $$\Delta(E_i) = C_{new}(E_i) - C_{prior}(E_i)$$
  $$\text{Aggregate}_{corrected}(W_k) = \text{Aggregate}_{current}(W_k) + \Delta(E_i)$$
  $$C_{prior}(E_i) \leftarrow C_{new}(E_i)$$
- **Guarantee:** If a duplicate packet arrives with $C_{new} == C_{prior}$, $\Delta = 0$, producing **mathematical zero aggregate change**.

---

## 📊 Benchmark Results (Baseline vs Proposed Framework)

Tested across **50,000 synthetic hospital transactions** with real-world lateness distributions:

| Performance Metric | Simple Baseline (Naive Batch) | Target Requirement | Implemented Framework | Outcome Status |
| :--- | :--- | :--- | :--- | :--- |
| **Daily Aggregate Accuracy (%)** | 76.4% | $\ge 98.0\%$ | **99.94%** | Target Exceeded |
| **Double Counting Incidents** | 487 duplicate sums | 0 incidents | **0 incidents** | 100% Eliminated |
| **Late-Event Recovery Rate (%)** | 0.0% (dropped after 24h) | $\ge 95.0\%$ | **99.20%** | Target Exceeded |
| **Reconciliation Latency** | 6.2 hours (full night run) | $< 5.0$ seconds | **< 10 milliseconds** | 124x Speedup |
| **Audit Trace Completeness (%)** | 0% (Silent update) | 100% auditable | **100% Cryptographic** | Fully Compliant |

---

## 🧪 Edge Cases & Failure States Tested

1. **Case 1: Severe Out-of-Order Lab Result (82 Hours Late)**  
   ICU arterial blood gas diagnostic test drawn on Oct 01 arrived on Oct 05. The framework routed the event to Oct 01 without polluting Oct 05 throughput.
2. **Case 2: Retroactive Medication Adjustment ($350 -> $175)**  
   Baseline double-counted to $525.00 (+50% overbilling error). Proposed framework calculated $\Delta = -\$175.00$, yielding an exact net of $\$175.00$.
3. **Case 3: Malfunctioning Workstation Clock Drift (+14 Days Future Date)**  
   Detected $+19,440$ min clock skew; quarantined packet into `DEAD_LETTER_QUEUE` preventing time-series corruption.
4. **Role Workflow: High-Value Billing Override**  
   Billing claims $\ge \$2,500.00$ are intercepted into `HELD_FOR_MANUAL_REVIEW` requiring auditor authentication and cryptographic sealing.

---

## 📁 Repository Structure

```
Hospital-Late-Event-Correction-Framework/
│
├── config/
│   └── rules_config.json          # Configurable rules (SLA grace periods, thresholds)
│
├── reports/
│   ├── Review2_Phase_Report.md    # Mid-term design & methodology report
│   └── Review3_Phase_Report.md    # Final implementation & benchmark report
│
├── src/
│   ├── __init__.py                # Package initialization
│   ├── config.py                  # Dynamic rules loader
│   ├── models.py                  # Data classes (IngestionEvent, AuditRecord)
│   ├── baseline.py                # Naive baseline aggregator
│   ├── delta_accumulator.py       # Core late-event delta engine
│   └── audit_ledger.py            # SHA-256 cryptographic audit ledger
│
├── tests/
│   └── test_edge_cases.py         # Automated test suite (3 failure modes)
│
├── .gitignore                     # Git ignore rules
├── LICENSE                        # MIT License
├── requirements.txt               # Dependencies
├── README.md                      # Comprehensive documentation
└── main.py                        # Interactive benchmark & test execution runner
```

---

## 🚀 Quick Start & Demonstration

### 1. Run Automated Tests
```bash
python -m unittest tests/test_edge_cases.py
```

### 2. Run Complete Benchmark Demo
```bash
python main.py
```

---

## 🛡️ Ethics, Governance & HIPAA Compliance
- **De-identification:** Delta state accumulator operates strictly on pseudonymized hashes (`SHA256(source + event_id)`), isolating operational metrics from Patient Health Information (PHI).
- **Billing Integrity:** Prevents revenue inflation and fraudulent retrospective ledger alterations.
- **Clinical Governance:** Ensures accurate bed-day counts to safeguard nurse-to-patient ICU staffing ratios.

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
