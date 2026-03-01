from sqlalchemy import LargeBinary
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from .db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(32), nullable=False)              # scan/extract/embed/plan/apply
    status = Column(String(16), nullable=False)            # queued/running/done/failed
    root_path = Column(Text, nullable=False)
    mode = Column(String(64), nullable=False)              # incremental/full o params (limit)
    stats_json = Column(Text, nullable=True)
    error = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FileEntry(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(Text, nullable=False, unique=True, index=True)
    root_path = Column(Text, nullable=False, index=True)

    size_bytes = Column(Integer, nullable=False)
    mtime = Column(Integer, nullable=False)
    ctime = Column(Integer, nullable=False)
    sha256 = Column(String(64), nullable=True)
    mimetype = Column(String(128), nullable=True)
    ext = Column(String(32), nullable=True)

    status = Column(String(16), nullable=False, default="active")
    last_seen_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    content_text = Column(Text, nullable=True)
    content_status = Column(String(16), nullable=False, default="pending")  # pending/ok/unsupported/error
    content_error = Column(Text, nullable=True)

    embedding = Column(LargeBinary, nullable=True)  # bytes
    embedding_model = Column(String(64), nullable=True)
    embedding_dim = Column(Integer, nullable=True)
    embedding_status = Column(String(16), nullable=False, default="pending")  # pending/ok/error
    embedding_error = Column(Text, nullable=True)

    # A2: marca artefactos generados / cache / build / simulación
    is_generated = Column(Boolean, nullable=False, default=False, index=True)


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    root_path = Column(Text, nullable=False, index=True)
    policy = Column(String(64), nullable=False, default="default")
    status = Column(String(16), nullable=False, default="done")  # done/failed

    plan_json = Column(Text, nullable=False)
    error = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OpJournal(Base):
    __tablename__ = "op_journal"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, nullable=False, index=True)
    status = Column(String(16), nullable=False, default="done")  # done/failed

    ops_json = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())