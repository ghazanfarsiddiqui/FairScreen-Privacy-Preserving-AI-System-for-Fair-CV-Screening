import streamlit as st
from src.cv_parser import extract_text_from_pdf, redact_personal_info
from src.ranker import score_candidates
from src.fairness_eval import fairness_invariance_test

st.set_page_config(page_title="FairScreen", page_icon="🛡️", layout="wide")
st.title("🛡️ FairScreen Project By Ghazanfar Anees Siddiqui")

@st.cache_data(show_spinner=False)
def cached_extract(pdf_bytes: bytes) -> str:
    # Wrap bytes into an in-memory file-like object for pdfplumber
    import io
    return extract_text_from_pdf(io.BytesIO(pdf_bytes))

@st.cache_data(show_spinner=False)
def cached_anonymize(text: str) -> str:
    return redact_personal_info(text)

tab1, tab2 = st.tabs(["🔍 Screening (RAG + Calibrated)", "⚖️ Fairness Report"])

with tab1:
    job_desc = st.text_area("Job Description", height=160)

    rag_top_k = st.slider("RAG: top-k relevant CV sections", min_value=2, max_value=12, value=5, step=1)

    uploaded_files = st.file_uploader("Upload CV PDFs", type="pdf", accept_multiple_files=True)

    if st.button("Run GDPR Scan → RAG Retrieval → Hybrid Score → Calibration"):
        if not uploaded_files or not job_desc.strip():
            st.warning("Please provide a job description and upload at least 1 CV.")
        else:
            st.info("Pipeline: PDF → Cache → PII Removal → Cache → RAG Retrieval → Hybrid Score → Calibration")

            processed = []
            progress = st.progress(0.0)

            for i, pdf in enumerate(uploaded_files):
                pdf_bytes = pdf.getvalue()

                raw_text = cached_extract(pdf_bytes)
                safe_text = cached_anonymize(raw_text)

                processed.append({"filename": pdf.name, "text": safe_text})
                progress.progress((i + 1) / len(uploaded_files))

            results = score_candidates(job_desc, processed, rag_top_k=rag_top_k)

            st.success("Done. Results (calibrated across candidates).")

            for r in results:
                with st.expander(f"✅ {r['filename']} — Final {r['score']}% | Semantic {r['semantic_score']}% | Skills {r['skill_score']}%"):
                    cols = st.columns([1, 1])

                    with cols[0]:
                        st.markdown("### Skill Match (Structured)")
                        st.write("**Job skills:**", r["job_skills"])
                        st.write("**CV skills (from RAG text):**", r["cv_skills"])
                        st.write("**Common:**", r["overlap"]["common"])
                        st.write("**Missing:**", r["overlap"]["missing"])

                    with cols[1]:
                        st.markdown("### RAG Evidence: Retrieved CV Sections")
                        if r["rag_chunks"]:
                            for i, ch in enumerate(r["rag_chunks"]):
                                score = r["rag_chunk_scores"][i] if i < len(r["rag_chunk_scores"]) else None
                                if score is not None:
                                    st.caption(f"Chunk similarity: {round(score*100, 1)}%")
                                st.write(ch)
                        else:
                            st.caption("No chunks retrieved; fallback to full text.")

                    st.markdown("### Anonymized Preview (Full CV)")
                    st.caption(r["preview"])

with tab2:
    st.subheader("Fairness Invariance Test (Perturbation-based)")
    st.write(
        "Injects sensitive identifiers into the same content and measures score deviation. "
        "Lower deviation = more invariant/fair."
    )

    job = st.text_area("Job text for fairness test:", "Looking for a Python engineer with Docker and data skills.", height=120)
    base_cv = st.text_area("Base CV text for fairness test:", "Python developer with Docker and Linux. Built ML pipelines using pandas and numpy.", height=120)

    if st.button("Run Fairness Test"):
        report = fairness_invariance_test(job, base_cv)
        st.success("Fairness report generated.")
        st.write("Base score:", round(report["base_score"] * 100, 2), "%")
        st.write("Scores (base + perturbed):", [round(x * 100, 2) for x in report["scores"]])
        st.write("Max diff:", round(report["max_diff"] * 100, 3), "%")
        st.write("Mean diff:", round(report["mean_diff"] * 100, 3), "%")