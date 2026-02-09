import statistics
from src.ranker import hybrid_score_from_text

SENSITIVE_PERTURBATIONS = [
    "My name is John Smith from London. Email: john@email.com Phone: 555-0199. ",
    "My name is Fatima Khan from Karachi. Email: fatima@email.com Phone: 555-0199. ",
    "My name is Maria Rossi from Naples. Email: maria@email.com Phone: 555-0199. ",
]

def fairness_invariance_test(job_desc: str, base_cv_text: str):
    """
    Measures how much the score changes when we inject sensitive info.
    Lower change = more invariant/fair.
    """
    # base score
    semantic, skill_s, base, *_ = hybrid_score_from_text(job_desc, base_cv_text)

    scores = [base]
    for prefix in SENSITIVE_PERTURBATIONS:
        semantic, skill_s, s, *_ = hybrid_score_from_text(job_desc, prefix + base_cv_text)
        scores.append(s)

    diffs = [abs(x - base) for x in scores[1:]]
    return {
        "base_score": base,
        "scores": scores,
        "max_diff": max(diffs) if diffs else 0.0,
        "mean_diff": statistics.mean(diffs) if diffs else 0.0,
    }

if __name__ == "__main__":
    job = "Looking for a Python engineer with Docker, Linux and data science skills."
    cv = "Experienced Python developer. Built Dockerized ML pipelines. Strong Linux and Git. Worked with pandas and numpy."
    report = fairness_invariance_test(job, cv)
    print(report)
