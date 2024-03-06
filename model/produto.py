
from config.db import engine, meta_data

from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import Date, Integer, String, Boolean, NVARCHAR
produto = Table("produto", meta_data,
    Column("id", Integer, primary_key=True),
    Column("nome", String(255)),
    Column("desconto", String(255)),
    Column("preco", String(255)),
    Column("descricao", String(255)),
    Column("data_cadastro", Date),
    Column("ativo", Boolean),
    Column("categoria", NVARCHAR(255)),
    Column("miniatura", NVARCHAR(255)),
)

meta_data.create_all(engine)