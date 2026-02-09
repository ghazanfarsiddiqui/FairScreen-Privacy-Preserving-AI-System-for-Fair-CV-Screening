from sentence_transformers import SentenceTransformer, util
from src.skills import extract_skills, skill_overlap
from src.retrieval import retrieve_top_k
from src.calibration import minmax_calibrate

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

def hybrid_score_from_text(job_desc: str, text: str):
    # semantic score
    job_emb = model.encode(job_desc, convert_to_tensor=True)
    txt_emb = model.encode(text, convert_to_tensor=True)
    semantic = util.cos_sim(job_emb, txt_emb).item()

    # skill overlap
    job_sk = extract_skills(job_desc)
    cv_sk = extract_skills(text)
    overlap = skill_overlap(job_sk, cv_sk)
    skill_score = (overlap["common_count"] / overlap["job_count"]) if overlap["job_count"] else 0.0

    combined = (0.65 * semantic) + (0.35 * skill_score)
    return semantic, skill_score, combined, job_sk, cv_sk, overlap

def score_candidates(job_description, candidates_list, rag_top_k: int = 5):
    """
    candidates_list: [{'filename': '...', 'text': '...'}] where text is anonymized.
    RAG: retrieve top-k relevant chunks per candidate before scoring.
    Calibration: normalize combined scores across all candidates.
    """
    rows = []
    raw_combined = []

    # 1) compute raw scores using retrieved (job-relevant) text
    for c in candidates_list:
        top_chunks, top_chunk_scores = retrieve_top_k(job_description, c["text"], model, top_k=rag_top_k)

        # If retrieval found nothing, fallback to full text
        rag_text = "\n".join(top_chunks) if top_chunks else c["text"]

        semantic, skill_s, combined, job_sk, cv_sk, overlap = hybrid_score_from_text(job_description, rag_text)

        raw_combined.append(float(combined))
        rows.append({
            "filename": c["filename"],
            "rag_text": rag_text,
            "rag_chunks": top_chunks,
            "rag_chunk_scores": top_chunk_scores,
            "semantic_raw": float(semantic),
            "skill_raw": float(skill_s),
            "combined_raw": float(combined),
            "job_skills": job_sk,
            "cv_skills": cv_sk,
            "overlap": overlap,
            "preview": c["text"][:240] + "..."
        })

    # 2) calibrate within this candidate pool
    calibrated = minmax_calibrate(raw_combined)

    # 3) attach final calibrated score
    for i, r in enumerate(rows):
        r["score"] = round(calibrated[i] * 100, 1)              # final
        r["semantic_score"] = round(r["semantic_raw"] * 100, 1) # raw semantic (still useful)
        r["skill_score"] = round(r["skill_raw"] * 100, 1)       # raw skill overlap

    return sorted(rows, key=lambda x: x["score"], reverse=True)