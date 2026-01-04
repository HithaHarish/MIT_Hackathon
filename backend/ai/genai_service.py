import subprocess
import json

def derive_metadata(df, dq_scores):
    column_nulls = df.isnull().sum()
    total_rows = len(df)

    recoverable = []
    non_recoverable = []

    for col, null_count in column_nulls.items():
        if null_count == 0:
            continue

        null_pct = round((null_count / total_rows) * 100, 2)

        # Business rules (deterministic)
        if col.lower() in ["address", "email", "phone", "city", "country"]:
            recoverable.append({
                "field": col,
                "issue": f"{null_pct}% missing values",
                "reason": "Can be enriched from customer onboarding or external reference data"
            })
        elif col.lower() in ["transaction_id", "customer_id", "merchant_id"]:
            non_recoverable.append({
                "field": col,
                "issue": f"{null_pct}% missing values",
                "reason": "Core identifier missing — requires upstream system correction"
            })
        else:
            recoverable.append({
                "field": col,
                "issue": f"{null_pct}% missing values",
                "reason": "Likely recoverable through reprocessing or validation rules"
            })

    return {
        "recoverable_issues": recoverable,
        "non_recoverable_issues": non_recoverable,
        "low_dimensions": [k for k, v in dq_scores.items() if v is not None and v < 85]
    }


def generate_ai_summary(df, dq_scores: dict, dataset_name: str) -> str:
    metadata = derive_metadata(df, dq_scores)

    prompt = f"""
    You are a senior data governance and regulatory compliance expert.

    Dataset Name: {dataset_name}

    Data Quality Scores:
    {json.dumps(dq_scores, indent=2)}

    Derived Metadata (DO NOT IGNORE):
    {json.dumps(metadata, indent=2)}

    Your task is to generate a DATA QUALITY ASSESSMENT REPORT.

    STRICT FORMAT (follow exactly):

    1. Executive Summary
    - One short paragraph summarizing overall data health.

    2. Recoverable Data Quality Issues
    - Bullet list
    - Format: Field → Issue → Why recoverable → How to fix

    3. Non-Recoverable Data Quality Issues
    - Bullet list
    - Format: Field → Issue → Risk → Required action

    4. Dimension-wise Recommendations
    - Mention ONLY dimensions listed in low_dimensions
    - Explain impact in business or regulatory terms

    5. Regulatory & Operational Impact
    - Mention compliance, reporting, fraud, or analytics impact
    - Use dataset-specific language

    RULES:
    - Use ONLY provided metadata
    - Do NOT invent fields
    - Do NOT generalize
    - Do NOT mention raw data
    - Write for non-technical stakeholders
    """

    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt,
        capture_output=True,
        text=True
    )

    return result.stdout.strip()
