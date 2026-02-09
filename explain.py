from sentence_transformers import util
import numpy as np

def chunk_text(text: str, max_chars: int = 450) -> list[str]:
    """
    Split resume into digestible chunks for explanation.
    Character chunks are simple and robust for PDFs.
    """
    text = (text or "").replace("\n", " ").strip()
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i + max_chars].strip()
        if chunk:
            chunks.append(chunk)
        i += max_chars
    return chunks[:30]  # safety limit

def top_evidence(job_desc: str, cv_text: str, model, top_k: int = 3):
    """
    Returns top resume chunks most similar to job description.
    This is the explainability evidence.
    """
    chunks = chunk_text(cv_text)
    if not chunks:
        return []

    job_emb = model.encode(job_desc, convert_to_tensor=True)
    chunk_emb = model.encode(chunks, convert_to_tensor=True)

    scores = util.cos_sim(job_emb, chunk_emb).cpu().numpy().flatten()
    top_idx = np.argsort(scores)[::-1][:top_k]

    evidence = []
    for idx in top_idx:
        evidence.append({
            "score": float(scores[int(idx)]),
            "snippet": chunks[int(idx)]
        })
    return evidence
