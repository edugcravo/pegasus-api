from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from schema.armazenamento_schema import armazenamento_schema
from config.db import engine
from model.armazenamento import armazenamento


armazenamento_router = APIRouter(
    prefix="/armazenamento",
    tags=["Armazenamento"],
)

@armazenamento_router.post("/cadastrar")
async def cadastrar_armazenamento(armazenamentoSchema: armazenamento_schema):
    with engine.connect() as conn:
        try:
            dados = armazenamentoSchema.dict()
            conn.execute(armazenamento.insert().values(dados))
            conn.commit()
            return {'status': 200,'message': 'Armazenamento cadastrado com sucesso'}
        except Exception as e:
            return {'status': 500,'message': 'Erro ao cadastrar armazenamento'}
        

@armazenamento_router.get("/listar")
async def listar_armazenamento():
    with engine.connect() as conn:
        try:
            result = conn.execute(armazenamento.select()).fetchall()
            result_list = [dict(row._asdict()) for row in result]

            # Convert each row to a dictionary

            return {'result': result_list}
        except Exception as e:
            return {'error': str(e)}