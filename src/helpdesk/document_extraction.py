from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(pdf_content: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_content))
    text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not text:
        raise ValueError("PDF contains no extractable text.")
    return text