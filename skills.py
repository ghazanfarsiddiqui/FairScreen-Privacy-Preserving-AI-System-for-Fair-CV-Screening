import re
from rapidfuzz import fuzz

# A practical skills dictionary (extend anytime)
SKILLS = sorted(set([
    # Programming
    "python", "java", "c++", "sql", "javascript", "typescript",
    # Data/AI
    "machine learning", "deep learning", "nlp", "pandas", "numpy",
    "scikit-learn", "pytorch", "torch", "tensorflow",
    "data analysis", "data science", "statistics",
    # Backend/DevOps
    "docker", "kubernetes", "linux", "git", "rest", "fastapi", "flask",
    "microservices", "ci/cd", "cloud", "aws", "azure", "gcp",
    # Systems
    "systems engineering", "requirements engineering", "testing", "qa"
]))

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#/\s\-\.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_skills(text: str, threshold: int = 90) -> list[str]:
    """
    Hybrid extraction:
    - Exact match for single-token skills (python, docker, sql, etc.)
    - Fuzzy match for multi-word skills (systems engineering, machine learning)
    """
    t = normalize(text)

    found = set()

    # quick exact token matching
    tokens = set(t.split())
    for s in SKILLS:
        s_norm = normalize(s)
        if " " not in s_norm:
            if s_norm in tokens:
                found.add(s)
        else:
            # fuzzy match multi-word skills by scanning text windows
            if s_norm in t:
                found.add(s)
            else:
                if fuzz.partial_ratio(s_norm, t) >= threshold:
                    found.add(s)

    return sorted(found)

def skill_overlap(job_skills: list[str], cv_skills: list[str]) -> dict:
    job_set = set([normalize(x) for x in job_skills])
    cv_set = set([normalize(x) for x in cv_skills])

    common = sorted(job_set.intersection(cv_set))
    missing = sorted(job_set.difference(cv_set))

    return {
        "common": common,
        "missing": missing,
        "job_count": len(job_set),
        "cv_count": len(cv_set),
        "common_count": len(common)
    }