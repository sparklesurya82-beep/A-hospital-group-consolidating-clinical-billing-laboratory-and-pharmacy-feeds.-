# REVIEW 2 PHASE REPORT: DETAILED DESIGN & MID-TERM PROTOTYPE

**Project Title:** Late-Event Correction Framework Updates Aggregates for Hospital Group Consolidating Clinical, Billing, Laboratory, and Pharmacy Feeds  
**Student Name:** M. Jayashri  
**Register Number:** 24111302  
**Department:** Computer Science & Engineering (Cohort C28)  

---

## 1. Scenario Definition & Multi-Feed Pipeline
In modern healthcare systems, operational decisions rely on consolidated multi-source event feeds:
- **Clinical EHR:** Admission, discharge, transfer (ADT) logs, patient bed-days.
- **Hospital Billing:** Electronic Data Interchange (EDI 837/835), charge captures, claims.
- **Laboratory (LIMS):** HL7 v2 / FHIR diagnostic orders and test panel results.
- **Pharmacy Feeds:** Script center dispensation, barcode medication administration (BCMA).

### The Late-Event Problem:
Due to network partitions, distributed asynchronous processing, and off-hour batch syncs, records often arrive hours or days after the clinical event ($T_a \gg T_e$). Standard daily reporting closed at 23:59:59 fails because arriving late events either get dropped (revenue/patient leakage) or appended naively to the current day, introducing distortion and severe double-counting.

---

## 2. Baseline Method & Its Flaws
The baseline implements the naive daily batch aggregator:
- `Aggregate = Aggregate + Value` applied blindly on arrival.
- Drops records arriving outside the 24-hour window.
- Retrospective updates cause double counting.

---

## 3. Mathematical & Algorithmic Formulation
- **Deterministic Idempotency Key:**
  `K_idemp = SHA256(source_feed || event_id || metric_name)`
- **Delta Arithmetic:**
  `Delta = C_new - C_prior`
  `Aggregate_Corrected(W_k) = Aggregate_Current(W_k) + Delta`
  `C_prior <- C_new`
- **Zero Double Counting Guarantee:**
  When a duplicate packet arrives with equal value, `Delta = 0.0`. Aggregate remains intact.

---

## 4. Configurable Rules Engine (No Hardcoding)
All operational parameters reside in external JSON configuration:
- Clinical Grace Period: 72 hours
- Billing Grace Period: 168 hours (7 days)
- Laboratory Grace Period: 48 hours
- Pharmacy Grace Period: 24 hours
- Clock drift tolerance: 15 minutes
- Billing threshold for mandatory human sign-off: $2,500.00

---

## 5. Dual Organisational Roles
1. **Health Informatics Data Steward:** Manages ingestion telemetry, watermarks, dead-letter queue, and rules configuration.
2. **Hospital Billing Compliance Auditor:** Inspects retrospective deltas, authorizes high-value overrides, and reviews audit logs.
