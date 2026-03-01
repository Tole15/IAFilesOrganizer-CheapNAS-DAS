import os
import json
from dataclasses import dataclass
from typing import List, Dict, Any

ILLEGAL = '<>:"/\\|?*'

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def safe_exists(path: str) -> bool:
    return os.path.exists(path)

def add_suffix_if_exists(dst: str) -> str:
    """
    Si dst existe, agrega sufijo _1, _2, ... antes de la extensión.
    """
    if not os.path.exists(dst):
        return dst

    base, ext = os.path.splitext(dst)
    i = 1
    while True:
        candidate = f"{base}_{i}{ext}"
        if not os.path.exists(candidate):
            return candidate
        i += 1

def apply_plan(plan: dict, dry_run: bool = True) -> dict:
    """
    Ejecuta acciones move. No borra. No overwrite.
    Retorna journal dict con ops ejecutadas (o simuladas).
    """
    ops = []
    errors = []

    for a in plan.get("actions", []):
        if a.get("action") != "move":
            continue

        src = a["from"]
        dst = a["to"]
        dst_dir = a.get("mkdir") or os.path.dirname(dst)

        # Validación básica: evitar salirte del root
        root = plan["root_path"]
        # normaliza
        root_n = os.path.normpath(root)
        dst_n = os.path.normpath(dst)

        if not dst_n.startswith(root_n):
            errors.append({"src": src, "dst": dst, "error": "Destination outside root_path"})
            continue

        # Si src no existe, lo marcamos error (OneDrive etc.)
        if not os.path.exists(src):
            errors.append({"src": src, "dst": dst, "error": "Source not found"})
            continue

        # Crea carpeta
        if dry_run:
            ops.append({"op": "mkdir", "path": dst_dir})
        else:
            ensure_dir(dst_dir)

        # Evita overwrite
        final_dst = add_suffix_if_exists(dst)

        # Si ya está en el lugar final, skip
        if os.path.normpath(src) == os.path.normpath(final_dst):
            ops.append({"op": "skip", "src": src, "dst": final_dst, "reason": "already_in_place"})
            continue

        if dry_run:
            ops.append({"op": "move", "src": src, "dst": final_dst})
        else:
            # journal para undo: guardamos move original (dst final)
            os.replace(src, final_dst)  # move/rename atómico en mismo volumen
            ops.append({"op": "move", "src": src, "dst": final_dst})

    return {
        "dry_run": dry_run,
        "plan_root_path": plan.get("root_path"),
        "ops": ops,
        "errors": errors,
        "summary": {
            "mkdir": sum(1 for x in ops if x["op"] == "mkdir"),
            "move": sum(1 for x in ops if x["op"] == "move"),
            "skip": sum(1 for x in ops if x["op"] == "skip"),
            "errors": len(errors),
        }
    }