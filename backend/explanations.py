def generate_dqs_explanation_text():
    return """
VISA DATA QUALITY SCORE (DQS) — MEASUREMENT METHODOLOGY
====================================================

Purpose
-------
The Data Quality Score (DQS) provides a standardized, explainable, and
audit-friendly mechanism to assess the quality and operational readiness
of datasets used in payment systems. The scoring approach combines
formula-based metrics, schema validation, and rule-based checks aligned
with real-world payment workflows.

--------------------------------------------------
DATA QUALITY DIMENSIONS
--------------------------------------------------

1. Completeness
---------------
What it measures:
The extent to which expected data fields are populated across the dataset.

How it is measured:
Completeness is calculated as the percentage of non-null values across
all cells in the dataset. The metric considers missing values across
all columns, including identifiers, timestamps, and financial fields.

Formula:
Completeness = (1 - (Total Missing Cells / Total Cells)) × 100

Why it matters:
Missing data can disrupt transaction processing, reconciliation,
regulatory reporting, and downstream analytics.

--------------------------------------------------

2. Uniqueness
-------------
What it measures:
The degree to which records are duplicated within the dataset.

How it is measured:
Uniqueness is calculated by identifying duplicate rows using full-row
comparison. The proportion of duplicate records is subtracted from the
total row count to derive the uniqueness score.

Formula:
Uniqueness = (1 - (Duplicate Rows / Total Rows)) × 100

Why it matters:
Duplicate records can lead to double-counting, settlement mismatches,
and financial inconsistencies.

--------------------------------------------------

3. Validity
-----------
What it measures:
Whether data values conform to expected formats, data types, and
business constraints.

How it is measured:
Validity is assessed using schema-based validation and rule checks,
including:
- Email fields containing valid email patterns
- Amount fields containing numeric values greater than zero
- Date and timestamp fields conforming to datetime formats

Schema validation is performed using Pandera, with all validation
failures collected and quantified.

Formula:
Validity = (1 - (Invalid Records / Total Rows)) × 100

Why it matters:
Invalid data can break automated systems, violate regulatory standards,
and prevent reliable processing.

--------------------------------------------------

4. Accuracy (Estimated)
----------------------
What it measures:
The correctness of data values relative to expected real-world behavior.

How it is estimated:
True accuracy requires external ground truth, which is unavailable in
most operational systems. Industry practice estimates accuracy using
validity and logical consistency checks as a proxy.

In this implementation:
Accuracy score is derived directly from the Validity score.

Why it matters:
Accurate data underpins financial reporting, risk assessment, and
customer trust.

--------------------------------------------------

5. Consistency
--------------
What it measures:
Logical alignment between related data fields within the dataset.

How it is measured:
Full consistency validation requires end-to-end business workflows.
As a practical proxy, consistency is approximated using the average
of completeness and validity scores.

Formula:
Consistency = (Completeness + Validity) / 2

Why it matters:
Inconsistent data indicates upstream integration issues or process
misalignment across systems.

--------------------------------------------------

6. Timeliness
-------------
What it measures:
Whether data is processed and settled within expected service-level
timeframes.

How it is measured:
Timeliness is calculated by comparing transaction timestamps with
settlement dates. Delays are evaluated against dynamic SLA thresholds
based on payment channel (e.g., UPI, Card, Wire).

Records exceeding SLA-defined delays reduce the timeliness score.

Formula:
Timeliness = (1 - (Late Records / Total Rows)) × 100

Why it matters:
Delayed data impacts fraud detection, settlement accuracy, operational
visibility, and regulatory reporting.

--------------------------------------------------

7. Integrity
------------
What it measures:
Referential consistency across related datasets.

How it is measured:
Integrity checks verify that identifiers in the transaction dataset
(e.g., customer_id, merchant_id) exist in corresponding reference
datasets such as customer and merchant master data.

Broken references reduce the integrity score.

Formula:
Integrity = (1 - (Broken References / Total Rows)) × 100

Why it matters:
Broken references indicate serious data pipeline, governance, or control
failures and reduce trust in end-to-end data reliability.

--------------------------------------------------
COMPOSITE DATA QUALITY SCORE (DQS)
--------------------------------------------------

The overall DQS is computed as an aggregation of individual dimension
scores, providing a single, easy-to-interpret indicator of dataset
readiness while preserving transparency at the dimension level.

The modular design allows weighting, thresholding, and dimension
selection to be customized based on regulatory or business requirements.

--------------------------------------------------
PRIVACY & GOVERNANCE
--------------------------------------------------

- No raw transaction or customer data is stored.
- All processing is performed in-memory.
- Only metadata, quality metrics, and scores are generated.
- No personally identifiable information (PII) is retained or exposed.

End of Document
"""