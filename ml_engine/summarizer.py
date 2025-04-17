from transformers import pipeline
from pdfminer.high_level import extract_text
import logging

# Load the BERT-based summarization pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def extract_text_from_pdf(pdf_path, max_chars=3000):
    """
    Extract text from the first few pages of a PDF.
    """
    try:
        full_text = extract_text(pdf_path)
        return full_text[:max_chars]  # Truncate if it's too long
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return ""

def generate_summary(raw_text):
    """
    Generate a summary from a PDF document.
    """

    if not raw_text:
        return "Unable to extract or summarize content."

    # Hugging Face models usually require < 1024 tokens input.
    summary = summarizer(raw_text, max_length=150, min_length=40, do_sample=False)

    return summary[0]["summary_text"]
