import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check


# --------------------------------------------------
# CONFIGURATION (REAL-TIME READY)
# --------------------------------------------------

# SLA definitions (can be externalized in production)
PAYMENT_SLA_DAYS = {
    "UPI": 1,
    "CARD": 2,
    "WIRE": 3,
    "DEFAULT": 2
}

# --------------------------------------------------
# CORE FUNCTION
# --------------------------------------------------
def compute_dq_dimensions(
    df: pd.DataFrame,
    dataset_type: str,
    ref_customers=None,
    ref_merchants=None
):
    """
    Computes standard Data Quality dimensions using
    a hybrid approach:
    - Formula-based metrics
    - Rule-based validation
    - Schema enforcement
    - Proxy metrics where ground truth is unavailable
    """

    total_rows = len(df)
    total_cells = total_rows * len(df.columns)

    # ==================================================
    # 1. COMPLETENESS (FORMULA-BASED)
    # ==================================================
    null_cells = df.isnull().sum().sum()
    completeness = (
        round((1 - null_cells / total_cells) * 100, 2)
        if total_cells else 100.0
    )

    # ==================================================
    # 2. UNIQUENESS (FORMULA-BASED)
    # ==================================================
    duplicate_rows = df.duplicated().sum()
    uniqueness = (
        round((1 - duplicate_rows / total_rows) * 100, 2)
        if total_rows else 100.0
    )

    # ==================================================
    # 3. VALIDITY (SCHEMA + RULE BASED)
    # ==================================================
    invalid_count = 0

    try:
        schema_columns = {}

        for col in df.columns:
            col_lower = col.lower()

            # Email validation
            if "email" in col_lower:
                schema_columns[col] = Column(
                    pa.String,
                    checks=Check.str_contains("@"),
                    nullable=True
                )

            # Amount validation
            elif "amount" in col_lower:
                schema_columns[col] = Column(
                    pa.Float,
                    checks=Check.greater_than(0),
                    nullable=True
                )

            # Timestamp / date validation
            elif "date" in col_lower or "timestamp" in col_lower:
                schema_columns[col] = Column(
                    pa.DateTime,
                    nullable=True
                )

            # Default: allow nullable, no strict checks
            else:
                schema_columns[col] = Column(nullable=True)

        schema = DataFrameSchema(schema_columns, coerce=True)

        # Validate (lazy=True collects all failures)
        schema.validate(df, lazy=True)

        validity = 100.0

    except pa.errors.SchemaErrors as err:
        invalid_count = len(err.failure_cases)
        validity = (
            round((1 - invalid_count / total_rows) * 100, 2)
            if total_rows else 100.0
        )

    # ==================================================
    # 4. ACCURACY (PROXY)
    # ==================================================
    # True accuracy requires ground truth.
    # Industry practice: use validity as a proxy.
    accuracy = validity

    # ==================================================
    # 5. CONSISTENCY (LOGICAL PROXY)
    # ==================================================
    # Full consistency requires business workflows.
    # Proxy: average of completeness & validity.
    consistency = round((completeness + validity) / 2, 2)

    # ==================================================
    # 6. TIMELINESS (SLA-BASED, REAL-TIME READY)
    # ==================================================
    timeliness = None

    if (
        "transaction_timestamp" in df.columns and
        "settlement_date" in df.columns
    ):
        delays = (
            pd.to_datetime(df["settlement_date"], errors="coerce") -
            pd.to_datetime(df["transaction_timestamp"], errors="coerce")
        ).dt.days

        # Determine SLA dynamically if payment_channel exists
        if "payment_channel" in df.columns:
            sla_days = df["payment_channel"].map(
                lambda x: PAYMENT_SLA_DAYS.get(str(x).upper(), PAYMENT_SLA_DAYS["DEFAULT"])
            )
            late = delays > sla_days
        else:
            late = delays > PAYMENT_SLA_DAYS["DEFAULT"]

        timeliness = (
            round((1 - late.sum() / total_rows) * 100, 2)
            if total_rows else 100.0
        )

    # ==================================================
    # 7. INTEGRITY (REFERENTIAL CHECKS)
    # ==================================================
    integrity = None

    if dataset_type == "transaction":
        broken_refs = 0

        if ref_customers is not None and "customer_id" in df.columns:
            broken_refs += (~df["customer_id"].isin(ref_customers)).sum()

        if ref_merchants is not None and "merchant_id" in df.columns:
            broken_refs += (~df["merchant_id"].isin(ref_merchants)).sum()

        integrity = (
            round((1 - broken_refs / total_rows) * 100, 2)
            if total_rows else 100.0
        )

    # ==================================================
    # RETURN RESULT
    # ==================================================
    return {
        "Completeness": completeness,
        "Uniqueness": uniqueness,
        "Validity": validity,
        "Accuracy": accuracy,
        "Consistency": consistency,
        "Timeliness": timeliness,
        "Integrity": integrity
    }
