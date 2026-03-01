import os

def undo_ops(journal: dict, dry_run: bool = True) -> dict:
    """
    Revierte moves en orden inverso.
    Solo revierte ops con op=move.
    """
    ops = journal.get("ops", [])
    errors = []
    reverted = []

    for op in reversed(ops):
        if op.get("op") != "move":
            continue

        src = op["src"]   # original
        dst = op["dst"]   # actual location

        if not os.path.exists(dst):
            errors.append({"src": src, "dst": dst, "error": "Current file not found"})
            continue

        # No overwrite al regresar
        if os.path.exists(src):
            errors.append({"src": src, "dst": dst, "error": "Original destination already exists"})
            continue

        if dry_run:
            reverted.append({"op": "undo_move", "from": dst, "to": src})
        else:
            os.replace(dst, src)
            reverted.append({"op": "undo_move", "from": dst, "to": src})

    return {
        "dry_run": dry_run,
        "reverted": reverted,
        "errors": errors,
        "summary": {"undo_moves": len(reverted), "errors": len(errors)}
    }