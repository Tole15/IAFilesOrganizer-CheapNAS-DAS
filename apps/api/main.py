from fastapi import FastAPI
from packages.core.db import Base, engine
from packages.core.storage import ensure_dir
from apps.api.routes.scan import router as scan_router
from apps.api.routes.jobs import router as jobs_router
from apps.api.routes.files import router as files_router
from apps.api.routes.extract import router as extract_router
from apps.api.routes.embed import router as embed_router
from apps.api.routes.search import router as search_router
from apps.api.routes.stats import router as stats_router
from apps.api.routes.health import router as health_router
from apps.api.routes.plan import router as plan_router
from apps.api.routes.plans import router as plans_router
from apps.api.routes.apply import router as apply_router
from apps.api.routes.undo import router as undo_router


app = FastAPI(title="Smart Storage Organizer AI")

ensure_dir("./data")
Base.metadata.create_all(bind=engine)

app.include_router(scan_router)
app.include_router(jobs_router)
app.include_router(files_router)
app.include_router(extract_router)
app.include_router(embed_router)
app.include_router(search_router)
app.include_router(stats_router)
app.include_router(health_router)
app.include_router(plan_router)
app.include_router(plans_router)
app.include_router(apply_router)
app.include_router(undo_router)