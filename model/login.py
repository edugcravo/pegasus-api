from datetime import datetime

from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import Date, Integer, String, Time, VARCHAR, Boolean

from config.db import engine, meta_data

login = Table("login",meta_data,
    Column("id", Integer, primary_key=True),
    Column("username", String(255)),
    Column("password", String(255)),
    Column("email", String(255)),

)

meta_data.create_all(engine)