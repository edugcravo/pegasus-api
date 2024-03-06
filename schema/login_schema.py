from typing import Optional
from pydantic import BaseModel


class login_schema(BaseModel):
  id: Optional[int]
  username: str
  password: str
  email: str

class login_schema_in(BaseModel):
  username: str
  password: str

class token(BaseModel):
  token: str