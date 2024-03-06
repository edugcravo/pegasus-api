from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from schema.cores_schema import cores_schema
from config.db import engine
from model.cores import cores


cores_router = APIRouter(
    prefix="/cores",
    tags=["Cores"],
)

@cores_router.post("/cadastrar")
async def cadastrar_cores(coresSchema: cores_schema):
    with engine.connect() as conn:
        try:
            dados = coresSchema.dict()
            conn.execute(cores.insert().values(dados))
            conn.commit()
            return {'status': 200,'message': 'Cores cadastrado com sucesso'}
        except Exception as e:
            return {'status': 500,'message': 'Erro ao cadastrar cores'}
        

@cores_router.get("/listar")
async def listar_cores():
    with engine.connect() as conn:
        try:
            result = conn.execute(cores.select()).fetchall()
            result_list = [dict(row._asdict()) for row in result]

            # Convert each row to a dictionary

            return {'result': result_list}
        except Exception as e:
            return {'error': str(e)}