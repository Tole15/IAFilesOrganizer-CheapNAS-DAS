import re

_CID_RE = re.compile(r"\(cid:\d+\)")
_WS_RE = re.compile(r"[ \t]+")

def clean_text(s: str, max_len: int = 20000) -> str:
    s = (s or "").strip()
    s = _CID_RE.sub(" ", s)          
    s = s.replace("\u00ad", "")      
    s = _WS_RE.sub(" ", s)
    if len(s) > max_len:
        s = s[:max_len]
    return s