from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from model.associacao import produto_cores, produto_armazenamento, produto_imagens
from router.login.routes import login_router
from router.produto.routes import produto_router
from router.armazenamento.routes import armazenamento_router
from router.cores.routes import cores_router
from config.db import engine

from model.imagens import imagens

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(login_router)
app.include_router(produto_router)
app.include_router(armazenamento_router)
app.include_router(cores_router)

