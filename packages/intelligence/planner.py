import os
from datetime import datetime
from packages.intelligence.openai_planner import plan_for_file

ILLEGAL = '<>:"/\\|?*'
BAD_SUBFOLDERS = {"docs", "files", "misc", "stuff", "other", "document", "documents"}


def sanitize_segment(s: str) -> str:
    s = (s or "").strip().replace(" ", "_")
    for ch in ILLEGAL:
        s = s.replace(ch, "")
    s = s.strip("._")
    return s[:80] if s else "unknown"


def canonical_category(cat: str) -> str:
    """
    Normaliza para evitar explosión de categorías por variaciones mínimas.
    Mantiene libertad del LLM, pero reduce duplicados tipo:
    embedded_systems vs embedded_system, documentation vs docs, etc.
    """
    cat = sanitize_segment(cat).lower()

    cat = cat.replace("systems", "system")
    cat = cat.replace("documents", "docs")
    cat = cat.replace("documentation", "docs")

    cat = cat.replace("datasheet", "datasheets")

    return cat[:32] if cat else "misc"


def sanitize_filename(name: str, ext: str) -> str:
    name = (name or "").strip().replace(" ", "_")
    for ch in ILLEGAL:
        name = name.replace(ch, "")
    name = name.strip("._")

    if ext:
        if not name.lower().endswith("." + ext.lower()):
            name = f"{name}.{ext}"
    else:
        pass

    if len(name) > 120:
        if ext:
            base = name[: (120 - (len(ext) + 1))]
            name = f"{base}.{ext}"
        else:
            name = name[:120]

    return name or f"untitled.{ext}"


def build_plan(root_path: str, policy: str, files: list[dict]) -> dict:
    """
    Construye plan de organización (dry-run):
    - category libre (LLM), pero canonicalizada y acotada
    - subfolders máx 2 niveles (para evitar árboles profundos)
    - nombres sanitizados (Windows-safe)
    """
    actions = []
    conflicts = []
    proposed_targets = set()

    for f in files:
        fid = f["file_id"]
        path = f["path"]
        ext = (f.get("ext") or "").lower().lstrip(".")
        mimetype = f.get("mimetype") or ""
        preview = f.get("content_preview") or ""

        rec = plan_for_file(
        path=path, ext=ext, mimetype=mimetype, preview=preview,
        root_path=root_path, policy=policy
        )

        category = canonical_category(rec.get("category", "misc"))

        raw_subfolders = rec.get("suggested_subfolders") or []
        subfolders = [sanitize_segment(x).lower() for x in raw_subfolders if x]
        subfolders = [s for s in subfolders if s and s not in BAD_SUBFOLDERS]

       
        subfolders = [s[:32] for s in subfolders[:2]]

        suggested_filename = sanitize_filename(
            rec.get("suggested_filename", os.path.basename(path)),
            ext=ext,
        )

        target_dir = os.path.join(root_path, category, *subfolders)
        target_path = os.path.join(target_dir, suggested_filename)

        if target_path in proposed_targets:
            conflicts.append(
                {
                    "type": "duplicate_target_in_plan",
                    "to": target_path,
                    "resolution": "append_suffix",
                }
            )
            base, dot, ex = suggested_filename.rpartition(".")
            if dot:
                suggested_filename = f"{base}_{fid}.{ex}"
            else:
                suggested_filename = f"{suggested_filename}_{fid}"
            target_path = os.path.join(target_dir, suggested_filename)

        proposed_targets.add(target_path)

        actions.append(
            {
                "action": "move",
                "file_id": fid,
                "from": path,
                "to": target_path,
                "mkdir": target_dir,
                "confidence": float(rec.get("confidence", 0.5)),
                "rationale": rec.get("rationale", []),
            }
        )

    plan = {
        "root_path": root_path,
        "policy": policy,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "files_considered": len(files),
            "actions": len(actions),
            "conflicts": len(conflicts),
        },
        "actions": actions,
        "conflicts": conflicts,
    }
    return plan