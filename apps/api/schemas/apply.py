from pydantic import BaseModel

class ApplyRequest(BaseModel):
    plan_id: int
    dry_run: bool = True

class ApplyResponse(BaseModel):
    plan_id: int
    dry_run: bool
    summary: dict
    errors: list