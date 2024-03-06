from config.db import engine, meta_data

from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import Integer, String, Boolean

cores = Table("cores", meta_data,
    Column("id", Integer, primary_key=True),
    Column("nome", String(255)),
    Column("hexadecimal", String(255)),
    Column("ativo", Boolean)
)

meta_data.create_all(engine)