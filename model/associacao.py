from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.sql.sqltypes import Integer
from config.db import meta_data

from config.db import engine, meta_data

produto_cores = Table(
    "produto_cores",
    meta_data,
    Column("produto_id", Integer),
    Column("cores_id", Integer)
)

produto_armazenamento = Table(
    "produto_armazenamento",
    meta_data,
    Column("produto_id", Integer),
    Column("armazenamento_id", Integer),
)

produto_imagens = Table(
    "produto_imagens",
    meta_data,
    Column("produto_id", Integer ),
    Column("imagens_id", Integer),
)

meta_data.create_all(engine)