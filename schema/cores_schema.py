from typing import Optional
from pydantic import BaseModel


class cores_schema(BaseModel):
    id: Optional[int]
    nome: str
    hexadecimal: str
    ativo: bool