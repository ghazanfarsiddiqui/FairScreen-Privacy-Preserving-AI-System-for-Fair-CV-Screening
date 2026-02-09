import pdfplumber
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def extract_text_from_pdf(uploaded_file):
    text_content = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
    except Exception as e:
        print(f"PDF read error: {e}")
    return text_content

def redact_personal_info(text):
    results = analyzer.analyze(
        text=text,
        entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION"],
        language="en"
    )
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text
