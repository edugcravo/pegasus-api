from config.db import engine, meta_data

from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import  Date, Integer, String, NVARCHAR

imagens = Table("imagens", meta_data,
    Column("id", Integer, primary_key=True),
    Column("imagem", NVARCHAR(255)),
)

meta_data.create_all(engine)