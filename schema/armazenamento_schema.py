from typing import Optional
from pydantic import BaseModel


class armazenamento_schema(BaseModel):
    id: Optional[int]
    quantidade: str