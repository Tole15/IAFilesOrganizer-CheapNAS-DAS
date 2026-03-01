from pydantic import BaseModel

class PlanRequest(BaseModel):
    root_path: str
    policy: str = "default"
    limit: int = 30
    exclude_globs: list[str] = [] 

class PlanResponse(BaseModel):
    job_id: int
    status: str