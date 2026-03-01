import os
import json
import re
from openai import OpenAI
from packages.core.config import OPENAI_PLAN_MODEL

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ILLEGAL = '<>:"/\\|?*'

SYSTEM = """You are a file organization planner.
Return ONLY a JSON object. No markdown, no code fences, no commentary.

The JSON MUST have keys:
- category: short label (1-3 words max)
- suggested_subfolders: array of folder names (0 to 2 items MAX)
- suggested_filename: file name with extension preserved
- confidence: number 0..1
- rationale: array of short strings

Hard constraints:
- Total folder depth must be <= 3:
  root / category / subfolder1 / subfolder2   (subfolders are optional)
- suggested_subfolders length MUST be 0, 1, or 2 (never more).
- Folder name rules:
  - ASCII if possible, use lowercase_with_underscores
  - 2..32 characters each
  - No illegal path characters: <>:"/\|?*
- category rules:
  - use lowercase_with_underscores
  - 2..32 characters
  - avoid pluralization variants; prefer singular (e.g., 'document' not 'documents')
- Filename rules:
  - use ASCII if possible, use underscores instead of spaces
  - preserve original extension
  - max length 80 chars
- Avoid generic file names or folders like 'document', 'file', 'misc', 'stuff', 'other', 'temp'; prefer descriptive labels based on content.

Category guidance:
- Infer the most appropriate top-level category based on the file's extension, semantic content, and original path context.
- Standardize on broad, stable top-level categories. Examples: 'hardware_design', 'software_project', 'academic', 'documentation', 'media', 'finance', 'personal'.
- If the original path or file indicates a specific technical domain (e.g., firmware, iot, pcb, fpga), group them logically. For example, place schematic files (.sch, .brd), HDL code (.vhd, .v), and related datasheets (.pdf) under a unified project subfolder within a broader category like 'engineering_project' or 'hardware_design'.
- Use specialized categories (e.g., 'embedded_system') ONLY when the content is highly specific and warrants separation from general software or hardware categories.
- Keep categories short and stable; avoid creating near-duplicates to prevent folder fragmentation.
"""

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)

def _first_json_block(text: str) -> str:
    text = (text or "").strip()
    m = _JSON_RE.search(text)
    if not m:
        raise ValueError(f"No JSON object found. Output starts: {text[:200]}")
    return m.group(0)

def _try_parse_json(s: str) -> dict:
    return json.loads(s)

def _repair_to_valid_json(bad_json_like_text: str) -> dict:
    """
    Pide al modelo que convierta la salida a JSON válido (sin texto extra).
    """
    repair_system = "You convert text into a valid JSON object. Return ONLY JSON."
    resp = client.responses.create(
        model=OPENAI_PLAN_MODEL,
        input=[
            {"role": "system", "content": repair_system},
            {"role": "user", "content": bad_json_like_text},
        ],
    )
    block = _first_json_block(resp.output_text)
    return _try_parse_json(block)

# --- AQUÍ ESTÁ LA CORRECCIÓN DE LA FIRMA ---
def plan_for_file(path: str, ext: str, mimetype: str, preview: str, root_path: str, policy: str) -> dict:
    # Preview recortado para costo/estabilidad
    preview = (preview or "").strip()
    if len(preview) > 4000:
        preview = preview[:4000]

    # Inyectamos root_path para que el modelo tenga más contexto
    user = {
        "root_path": root_path,
        "path": path,
        "ext": ext,
        "mimetype": mimetype,
        "content_preview": preview,
    }

    # Intento 1
    resp1 = client.responses.create(
        model=OPENAI_PLAN_MODEL,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
    )

    out1 = resp1.output_text
    block1 = _first_json_block(out1)

    try:
        return _try_parse_json(block1)
    except Exception:
        # Intento 2: prompt más estricto y explícito
        strict_user = (
            "Return a VALID JSON object only. Ensure commas and quotes are correct.\n"
            "JSON schema:\n"
            "{"
            "\"category\":\"...\","
            "\"suggested_subfolders\":[\"...\"],"
            "\"suggested_filename\":\"...\","
            "\"confidence\":0.0,"
            "\"rationale\":[\"...\"]"
            "}\n\n"
            f"Input:\n{json.dumps(user, ensure_ascii=False)}"
        )

        resp2 = client.responses.create(
            model=OPENAI_PLAN_MODEL,
            input=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": strict_user},
            ],
        )

        out2 = resp2.output_text
        block2 = _first_json_block(out2)

        try:
            return _try_parse_json(block2)
        except Exception:
            # Reparación final
            return _repair_to_valid_json(out2)