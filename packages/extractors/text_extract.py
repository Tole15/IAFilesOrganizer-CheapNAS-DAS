import pdfplumber
from docx import Document

SUPPORTED_TEXT_EXT = {"txt", "md", "py", "c", "h", "cpp", "json", "csv", "vhd", "vhdl", "sv", "v", "ini", "yaml", "yml"}

def extract_text(path: str, ext: str | None, mimetype: str | None) -> tuple[str | None, str, str | None]:
    """
    Returns: (text, status, error)
      status: ok / unsupported / error
    """
    try:
        e = (ext or "").lower()

        # Plain text family
        if e in SUPPORTED_TEXT_EXT:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(), "ok", None

        # PDF
        if e == "pdf" or (mimetype == "application/pdf"):
            parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    if t.strip():
                        parts.append(t)
            return "\n\n".join(parts), "ok", None

        # DOCX
        if e == "docx" or (mimetype and "wordprocessingml" in mimetype):
            doc = Document(path)
            text = "\n".join(p.text for p in doc.paragraphs if p.text)
            return text, "ok", None

        return None, "unsupported", None

    except Exception as ex:
        return None, "error", str(ex)