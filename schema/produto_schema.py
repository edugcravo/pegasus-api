from typing import List, Optional
from pydantic import BaseModel


class produto_schema(BaseModel):
  id: Optional[int]
  nome: str
  desconto: str
  preco: str
  cor: List[int]
  armazenamento: List[int]
  descricao: str
  data_cadastro: str
  ativo: bool
  imagens: List[str]
  categoria: str
  miniatura: str