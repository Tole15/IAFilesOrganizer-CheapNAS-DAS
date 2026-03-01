from pydantic import BaseModel

class UndoRequest(BaseModel):
    plan_id: int
    dry_run: bool = True

class UndoResponse(BaseModel):
    plan_id: int
    dry_run: bool
    summary: dict
    errors: list