from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from schema.produto_schema import produto_schema
from config.db import engine
from model.produto import produto
from model.imagens import imagens
from model.associacao import produto_cores, produto_armazenamento, produto_imagens


produto_router = APIRouter(
    prefix="/produto",
    tags=["Produto"],
)

@produto_router.post("/cadastrar")
async def cadastrar_produto(produtoSchema: produto_schema):
    with engine.connect() as conn:
        try:
            dados_produto = produtoSchema.dict()

            dados_produto['data_cadastro'] = datetime.today().strftime('%Y-%m-%d')

            cor = dados_produto.pop('cor')
            armazenamento = dados_produto.pop('armazenamento')
            imagens_dados = dados_produto.pop('imagens')
            miniatura = dados_produto.pop('miniatura')

            # Insere o produto na tabela de produtos
            result = conn.execute(produto.insert().values(dados_produto))
            id_produto = result.lastrowid

            # Insere as imagens na tabela de imagens
            imagens_ids = []
            for item in imagens_dados:
                result_img = conn.execute(imagens.insert().values(imagem=item))
                imagens_ids.append(result_img.lastrowid)

            # Associa as cores ao produto
            for item in cor:
                conn.execute(produto_cores.insert().values(produto_id=id_produto, cores_id=item))

            # Associa os armazenamentos ao produto
            for item in armazenamento:
                conn.execute(produto_armazenamento.insert().values(produto_id=id_produto, armazenamento_id=item))

            # Associa as imagens ao produto
            for img_id in imagens_ids:
                conn.execute(produto_imagens.insert().values(produto_id=id_produto, imagens_id=img_id))

            conn.commit()
            return {'status': 200,'message': 'Produto cadastrado com sucesso'}
        except Exception as e:
            print(f"Erro ao cadastrar produto: {e}")
            return {'status': 500,'message': 'Erro ao cadastrar produto'}
        


@produto_router.get("/listar")
async def listar_produtos():
    with engine.connect() as conn:
        try:
            result = conn.execute(produto.select()).fetchall()
            produtos = []

            # pegar as imagens, cores e armazenamentos e adicionar ao produto
            for item in result:
                imagens_produto = conn.execute(produto_imagens.select().where(produto_imagens.c.produto_id == item.id)).fetchall()
                imagens_produtos = []
                for img in imagens_produto:
                    img_data = conn.execute(imagens.select().where(imagens.c.id == img.imagens_id)).fetchone()
                    imagens_produtos.append(img_data.imagem)
                    if len(imagens_produtos) >= 4:
                        break

                cores_produto = conn.execute(produto_cores.select().where(produto_cores.c.produto_id == item.id)).fetchall()
                cores_produtos = [cores.cores_id for cores in cores_produto]

                armazenamentos_produto = conn.execute(produto_armazenamento.select().where(produto_armazenamento.c.produto_id == item.id)).fetchall()
                armazenamentos_produtos = [armazenamento.armazenamento_id for armazenamento in armazenamentos_produto]

                produtos.append({
                    'id': item.id,
                    'nome': item.nome,
                    'desconto': item.desconto,
                    'preco': item.preco,
                    'descricao': item.descricao,
                    'data_cadastro': item.data_cadastro,
                    'ativo': item.ativo,
                    'miniatura': item.miniatura,
                    'imagens': imagens_produtos,
                    'cores': cores_produtos,
                    'armazenamentos': armazenamentos_produtos
                })

            return {'status': 200, 'produtos': produtos}
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            return {'status': 500, 'message': 'Erro ao listar produtos'}

