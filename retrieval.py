from sentence_transformers import util
import numpy as np

def chunk_text(text: str, max_chars: int = 600) -> list[str]:
    text = (text or "").replace("\n", " ").strip()
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+max_chars].strip()
        if chunk:
            chunks.append(chunk)
        i += max_chars
    return chunks[:60]  # cap for speed

def retrieve_top_k(job_desc: str, cv_text: str, model, top_k: int = 5):
    """
    Returns (top_chunks, scores) where top_chunks are the most job-relevant sections.
    """
    chunks = chunk_text(cv_text)
    if not chunks:
        return [], []

    job_emb = model.encode(job_desc, convert_to_tensor=True)
    chunk_emb = model.encode(chunks, convert_to_tensor=True)

    scores = util.cos_sim(job_emb, chunk_emb).cpu().numpy().flatten()
    k = min(top_k, len(chunks))
    top_idx = np.argsort(scores)[::-1][:k]

    top_chunks = [chunks[int(i)] for i in top_idx]
    top_scores = [float(scores[int(i)]) for i in top_idx]
    return top_chunks, top_scores
