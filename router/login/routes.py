from datetime import timedelta
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
import httpx
from schema.login_schema import login_schema,login_schema_in
from config.db import engine
from model.login import login
from jose import JWTError, jwt
from datetime import datetime, timedelta
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext


login_router = APIRouter(
    prefix="/login",
    tags=["Login"],
)

SECRET_KEY = "a7db01243de9e2c43250f6f1825a367efc602db30526e624e45ee20b4394f77b"
ALGORITHM = "HS256"

# Configuração do esquema OAuth2 para autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




@login_router.post("/login")
async def logar(login_schema: login_schema_in):
    with engine.connect() as conn:
        try:
            dados = login_schema.dict()
            result = conn.execute(login.select().where(login.c.username==dados['username'])).fetchone()
            if result:
                result_dict = dict(result._asdict())
                print(result_dict['password'].encode())
                print(dados['password'].encode())
                if bcrypt.checkpw(dados['password'].encode(), result_dict['password'].encode()):
                    # Gerar token JWT
                    # Verificar as credenciais do usuário
                    # Se as credenciais forem válidas, gerar token JWT
                    # Exemplo simplificado:
                    access_token_expires = timedelta(minutes=30)
                    access_token = create_access_token(
                        data={"sub": dados['username']}, expires_delta=access_token_expires
                    )
                    return {"status": 200, "access_token": access_token, "token_type": "bearer"}
                else:
                    return {'status': 401,'message': 'Senha incorreta'}
            else:
                return {'status': 401,'message': 'Usuário não encontrado'}
        except Exception as e:
            return {'error': str(e)}
        

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verificar e decodificar o token JWT
    # Se o token for válido, retornar as informações do usuário
    # Exemplo simplificado:
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

@login_router.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {"data": 200}


@login_router.post("/cria-usuario")
async def cria_usuario(login_schema: login_schema):
    with engine.connect() as conn:
        try:
            dados = login_schema.dict()
            # Criptografar a senha antes de armazenar no banco de dados
            hashed_password = bcrypt.hashpw(dados['password'].encode(), bcrypt.gensalt())
            dados['password'] = hashed_password.decode()  # Armazenar a senha criptografada
            conn.execute(login.insert().values(dados))
            conn.commit()
            return {'data': 200,'message': 'Usuário criado com sucesso'}
        except Exception as e:
            return {'error': str(e)}

@login_router.put("/atualiza-usuario")
async def atualiza_usuario(login_schema: login_schema):
    with engine.connect() as conn:
        try:
            dados = login_schema.dict()
            # Criptografar a senha antes de armazenar no banco de dados
            hashed_password = bcrypt.hashpw(dados['password'].encode(), bcrypt.gensalt())
            dados['password'] = hashed_password.decode()  # Armazenar a senha criptografada
            conn.execute(login.update().where(login.c.username==dados['username']).values(dados))
            conn.commit()
            return {'message': 'Usuário atualizado com sucesso'}
        except Exception as e:
            return {'error': str(e)}
        
