from io import BytesIO
from typing import Optional


def parse_text_file(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


def parse_pdf_file(content: bytes) -> str:
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(BytesIO(content))
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)
    except Exception as e:
        return f"[PDF parse error: {str(e)}]"


def parse_docx_file(content: bytes) -> str:
    try:
        import docx
        doc = docx.Document(BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"[DOCX parse error: {str(e)}]"


def parse_document(filename: str, content: bytes) -> Optional[str]:
    lower_name = filename.lower()
    if lower_name.endswith(".txt"):
        return parse_text_file(content)
    if lower_name.endswith(".pdf"):
        return parse_pdf_file(content)
    if lower_name.endswith(".docx"):
        return parse_docx_file(content)
    return None
