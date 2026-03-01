from pydantic import BaseModel

class ExtractRequest(BaseModel):
    root_path: str
    limit: int = 500
    force: bool = False

class ExtractResponse(BaseModel):
    job_id: int
    status: str