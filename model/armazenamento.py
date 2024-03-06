

from config.db import engine, meta_data

from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import Integer, String

armazenamento = Table("armazenamento", meta_data,
    Column("id", Integer, primary_key=True),
    Column("quantidade", String(255)),
)

meta_data.create_all(engine)