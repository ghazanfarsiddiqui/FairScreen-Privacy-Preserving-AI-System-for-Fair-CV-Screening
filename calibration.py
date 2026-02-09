def minmax_calibrate(raw_scores: list[float]) -> list[float]:
    """
    Normalize a list of raw scores into 0..1 range using min-max scaling.
    Safe even when all values are equal.
    """
    if not raw_scores:
        return []

    mn = min(raw_scores)
    mx = max(raw_scores)

    # Avoid division by zero if all scores are identical
    if abs(mx - mn) < 1e-9:
        return [0.5 for _ in raw_scores]

    return [(s - mn) / (mx - mn) for s in raw_scores]