def compute_composite_dqs(scores: dict) -> float:
    weights = {
        "Completeness": 0.25,
        "Validity": 0.20,
        "Uniqueness": 0.15,
        "Integrity": 0.15,
        "Consistency": 0.10,
        "Timeliness": 0.10,
        "Accuracy": 0.05
    }

    dqs = 0
    for dim, weight in weights.items():
        value = scores.get(dim)
        if value is not None:
            dqs += value * weight

    return round(dqs, 2)
