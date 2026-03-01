from pydantic import BaseModel

class ScanRequest(BaseModel):
    root_path: str
    mode: str = "incremental"  # incremental/full

class ScanResponse(BaseModel):
    job_id: int
    status: str