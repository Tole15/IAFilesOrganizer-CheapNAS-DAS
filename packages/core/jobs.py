import json
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from packages.core.models import Job
from packages.scanner.scanner import scan_incremental


def create_scan_job(db: Session, root_path: str, mode: str) -> Job:
    job = Job(type="scan", status="queued", root_path=root_path, mode=mode)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_scan_job(db: Session, job_id: int) -> None:
    job = db.query(Job).filter(Job.id == job_id).one()
    job.status = "running"
    job.started_at = func.now()
    db.commit()

    try:
        if job.mode == "incremental":
            stats = scan_incremental(db, job, job.root_path)
        else:
            # Por ahora: full = incremental (afinamos luego)
            stats = scan_incremental(db, job, job.root_path)

        db.commit()
        job.status = "done"
        job.stats_json = json.dumps(stats)
        job.finished_at = func.now()
        db.commit()

    except Exception as e:
        db.rollback()
        job.status = "failed"
        job.error = str(e)
        job.finished_at = func.now()
        db.commit()


def create_extract_job(db: Session, root_path: str) -> Job:
    job = Job(type="extract", status="queued", root_path=root_path, mode="n/a")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_extract_job(db: Session, job_id: int, limit: int = 500, force: bool = False) -> None:
    from packages.core.models import FileEntry, Job
    from packages.extractors.text_extract import extract_text

    job = db.query(Job).filter(Job.id == job_id).one()
    job.status = "running"
    job.started_at = func.now()
    db.commit()

    stats = {"processed": 0, "ok": 0, "unsupported": 0, "error": 0, "skipped": 0}

    try:
        q = db.query(FileEntry).filter(
            FileEntry.root_path == job.root_path,
            FileEntry.status == "active",
            FileEntry.is_generated == False,
        )

        if not force:
            q = q.filter(FileEntry.content_status.in_(["pending", "error"]))

        rows = q.order_by(FileEntry.id.desc()).limit(limit).all()

        for f in rows:
            if (not force) and f.content_status == "ok":
                stats["skipped"] += 1
                continue

            text, st, err = extract_text(f.path, f.ext, f.mimetype)
            f.content_status = st
            f.content_error = err
            f.content_text = text if (st == "ok") else None

            stats["processed"] += 1
            if st == "ok":
                stats["ok"] += 1
            elif st == "unsupported":
                stats["unsupported"] += 1
            else:
                stats["error"] += 1

        db.commit()
        job.status = "done"
        job.stats_json = json.dumps(stats)
        job.finished_at = func.now()
        db.commit()

    except Exception as e:
        db.rollback()
        job.status = "failed"
        job.error = str(e)
        job.finished_at = func.now()
        db.commit()


def create_embed_job(db: Session, root_path: str, limit: int) -> Job:
    job = Job(type="embed", status="queued", root_path=root_path, mode=str(limit))
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_embed_job(db: Session, job_id: int, limit: int = 200) -> None:
    from packages.core.models import Job, FileEntry
    from packages.intelligence.openai_embed import embed_text
    from packages.intelligence.embedding_io import pack_embedding
    from packages.core.config import OPENAI_EMBED_MODEL

    job = db.query(Job).filter(Job.id == job_id).one()
    job.status = "running"
    job.started_at = func.now()
    db.commit()

    stats = {"processed": 0, "ok": 0, "error": 0, "skipped": 0}

    try:
        rows = (
            db.query(FileEntry)
            .filter(
                FileEntry.root_path == job.root_path,
                FileEntry.status == "active",
                FileEntry.content_status == "ok",
                FileEntry.is_generated == False,
            )
            .order_by(FileEntry.id.desc())
            .limit(limit)
            .all()
        )

        model = OPENAI_EMBED_MODEL

        for f in rows:
            if f.embedding_status == "ok" and f.embedding_model == model and f.embedding:
                stats["skipped"] += 1
                continue

            try:
                vec = embed_text(f.content_text or "", model=model)
                blob, dim = pack_embedding(vec)

                f.embedding = blob
                f.embedding_dim = dim
                f.embedding_model = model
                f.embedding_status = "ok"
                f.embedding_error = None
                stats["ok"] += 1

            except Exception as e:
                f.embedding_status = "error"
                f.embedding_error = str(e)
                stats["error"] += 1

            stats["processed"] += 1

        db.commit()
        job.status = "done"
        job.stats_json = json.dumps(stats)
        job.finished_at = func.now()
        db.commit()

    except Exception as e:
        db.rollback()
        job.status = "failed"
        job.error = str(e)
        job.finished_at = func.now()
        db.commit()


def create_plan_job(db: Session, root_path: str, policy: str, limit: int) -> Job:
    job = Job(type="plan", status="queued", root_path=root_path, mode=str(limit))
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_plan_job(db: Session, job_id: int, policy: str = "default", limit: int = 30, exclude_globs=None) -> int:
    """
    Genera un plan y lo guarda en tabla plans.
    Retorna plan_id.
    """
    from packages.core.models import Job, FileEntry, Plan
    from packages.intelligence.planner import build_plan

    job = db.query(Job).filter(Job.id == job_id).one()
    job.status = "running"
    job.started_at = func.now()
    db.commit()

    try:
        rows = (
            db.query(FileEntry)
            .filter(
                FileEntry.root_path == job.root_path,
                FileEntry.status == "active",
                FileEntry.content_status == "ok",
                FileEntry.is_generated == False,
            )
            .order_by(FileEntry.id.desc())
            .limit(limit)
            .all()
        )

        files = [
            {
                "file_id": r.id,
                "path": r.path,
                "ext": r.ext,
                "mimetype": r.mimetype,
                "content_preview": (r.content_text[:1200] if r.content_text else ""),
            }
            for r in rows
        ]

        plan_dict = build_plan(root_path=job.root_path, policy=policy, files=files)

        plan = Plan(
            root_path=job.root_path,
            policy=policy,
            status="done",
            plan_json=json.dumps(plan_dict, ensure_ascii=False),
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        job.status = "done"
        job.stats_json = json.dumps({"files": len(files), "plan_id": plan.id})
        job.finished_at = func.now()
        db.commit()

        return plan.id

    except Exception as e:
        db.rollback()
        job.status = "failed"
        job.error = str(e)
        job.finished_at = func.now()
        db.commit()
        raise