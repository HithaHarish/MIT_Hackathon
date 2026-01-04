def generate_dqs_explanation_text():
    return """
VISA DATA QUALITY SCORE (DQS) — EXPLANATION DOCUMENT
==================================================

Purpose
-------
The Data Quality Score (DQS) provides a standardized and objective way to
evaluate the reliability and readiness of datasets used in payment systems.
It enables both technical and non-technical stakeholders to quickly
understand data health and associated risks.

--------------------------------------------------
DATA QUALITY DIMENSIONS
--------------------------------------------------

1. Completeness
---------------
What it measures:
The extent to which required data fields are populated.

How it is calculated:
Completeness is calculated as the percentage of non-missing values across
all fields in the dataset.

Why it matters:
Missing data can lead to failed transactions, regulatory gaps, and
inaccurate analytics.

--------------------------------------------------

2. Uniqueness
-------------
What it measures:
The degree to which records are duplicated.

How it is calculated:
Uniqueness is derived by identifying duplicate rows and measuring their
proportion relative to total records.

Why it matters:
Duplicate records can cause double-counting, reconciliation errors, and
financial inconsistencies.

--------------------------------------------------

3. Validity
-----------
What it measures:
Whether data values conform to expected formats and ranges.

How it is calculated:
Validity checks include format validation (e.g., email structure),
range checks (e.g., transaction amount > 0), and allowed value checks.

Why it matters:
Invalid data can break downstream systems and violate regulatory standards.

--------------------------------------------------

4. Accuracy (Proxy)
-------------------
What it measures:
The correctness of data values.

How it is estimated:
Since ground truth is unavailable, accuracy is approximated using validity
checks as a proxy.

Why it matters:
Accurate data is essential for decision-making, risk assessment, and
customer trust.

--------------------------------------------------

5. Consistency
--------------
What it measures:
Logical alignment across related fields.

How it is calculated:
Consistency is approximated using the average of completeness and validity
scores.

Why it matters:
Inconsistent data indicates process breakdowns and integration issues.

--------------------------------------------------

6. Timeliness
-------------
What it measures:
Whether data is available within expected timeframes.

How it is calculated:
Timeliness is measured by comparing transaction timestamps with settlement
dates and identifying delayed records.

Why it matters:
Late data impacts fraud detection, settlement accuracy, and reporting.

--------------------------------------------------

7. Integrity
------------
What it measures:
Referential consistency across datasets.

How it is calculated:
Integrity checks ensure that identifiers such as customer IDs and merchant
IDs exist across related datasets.

Why it matters:
Broken references indicate serious data pipeline or governance issues.

--------------------------------------------------
COMPOSITE DATA QUALITY SCORE (DQS)
--------------------------------------------------

The overall DQS is a weighted aggregation of individual dimension scores.

Weighting Rationale:
- Completeness and Validity carry higher weight due to regulatory importance.
- Integrity is critical for cross-system reliability.
- Accuracy is weighted lower as it is estimated using proxies.

The composite score provides a single, easy-to-understand indicator of
dataset readiness while preserving transparency at the dimension level.

--------------------------------------------------
PRIVACY & GOVERNANCE
--------------------------------------------------

- No raw transaction data is stored.
- All processing occurs in-memory.
- Only metadata, metrics, and scores are generated.
- No personally identifiable information (PII) is exposed or retained.

End of Document
"""