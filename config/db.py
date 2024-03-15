from sqlalchemy import create_engine, MetaData

# Substitua os valores de 'username' e 'password' pelos fornecidos pela Hostinger
username = 'u846755771_admin'
password = 'BananacomRepolho123@'
database = 'u846755771_pegasus'

# String de conexão atualizada
engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost:3306/{database}")

meta_data = MetaData()