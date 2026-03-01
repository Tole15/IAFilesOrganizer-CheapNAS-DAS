import os
import mimetypes
import time
from sqlalchemy.orm import Session

from packages.core.models import FileEntry, Job
from .hashing import sha256_file



GENERATED_HINTS = [
    "/isim/", ".sim/", "/work/", "/precompiled.exe.sim/",
    "/xsim.dir/", "/modelsim/", "/questa/", "/xcelium.d/",
    "/.xil/", "/.git/", "/node_modules/", "/__pycache__/", "/.cache/",
    "/build/", "/dist/", "/_build/",
    "/.vs/", "/.idea/",
]


def is_generated_path(path: str) -> bool:
    p = (path or "").replace("\\", "/").lower()
    return any(h in p for h in GENERATED_HINTS)


def _now_epoch() -> int:
    return int(time.time())


def scan_incremental(db: Session, job: Job, root_path: str) -> dict:
    """
    Reglas:
    - Inserta archivo nuevo.
    - Si existe y cambió size o mtime -> recalcula hash y actualiza.
    - Si no cambió -> no recalcula hash.
    - Marca 'missing' a los que estaban en DB pero no se vieron en este job.
    - Marca is_generated automáticamente (A2).
    """
    stats = {"added": 0, "updated": 0, "unchanged": 0, "missing": 0, "errors": 0}
    seen_paths = set()

    for dirpath, _, filenames in os.walk(root_path):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            try:
                st = os.stat(full_path)
                size_bytes = int(st.st_size)
                mtime = int(st.st_mtime)
                ctime = int(st.st_ctime)

                ext = os.path.splitext(name)[1].lower().lstrip(".") or None
                mime, _ = mimetypes.guess_type(full_path)
                mime = mime or "application/octet-stream"

                entry = db.query(FileEntry).filter(FileEntry.path == full_path).one_or_none()
                seen_paths.add(full_path)

                if entry is None:
                    digest = sha256_file(full_path)
                    entry = FileEntry(
                        path=full_path,
                        root_path=root_path,
                        size_bytes=size_bytes,
                        mtime=mtime,
                        ctime=ctime,
                        sha256=digest,
                        mimetype=mime,
                        ext=ext,
                        status="active",
                        last_seen_job_id=job.id,
                        is_generated=is_generated_path(full_path),
                    )
                    db.add(entry)
                    stats["added"] += 1
                else:
                    changed = (entry.size_bytes != size_bytes) or (entry.mtime != mtime)
                    entry.root_path = root_path
                    entry.size_bytes = size_bytes
                    entry.mtime = mtime
                    entry.ctime = ctime
                    entry.mimetype = mime
                    entry.ext = ext
                    entry.status = "active"
                    entry.last_seen_job_id = job.id

                    
                    entry.is_generated = is_generated_path(full_path)

                    if changed:
                        entry.sha256 = sha256_file(full_path)
                        stats["updated"] += 1
                    else:
                        stats["unchanged"] += 1

            except Exception:
                stats["errors"] += 1

    
    q = db.query(FileEntry).filter(FileEntry.root_path == root_path)
    for entry in q:
        if entry.path not in seen_paths:
            entry.status = "missing"
            entry.last_seen_job_id = job.id
            stats["missing"] += 1

    return stats