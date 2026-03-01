from pydantic import BaseModel

class EmbedRequest(BaseModel):
    root_path: str
    limit: int = 200

class EmbedResponse(BaseModel):
    job_id: int
    status: str