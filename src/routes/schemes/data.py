from pydantic import BaseModel, Field
from typing import Optional, List

class ProcessRequest(BaseModel):
    """
    Request model for process data.
    """
    file_id: str
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0