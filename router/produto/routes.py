from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from schema.produto_schema import produto_schema
from config.db import engine
from model.produto import produto
from model.imagens import imagens
from model.associacao import produto_cores, produto_armazenamento, produto_imagens
from model.cores import cores
from model.armazenamento import armazenamento

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

            for item in result:
                # Buscar as imagens associadas ao produto
                imagens_produto = conn.execute(produto_imagens.select().where(produto_imagens.c.produto_id == item.id)).fetchall()
                imagens_produtos = []
                for img in imagens_produto:
                    img_data = conn.execute(imagens.select().where(imagens.c.id == img.imagens_id)).fetchone()
                    imagens_produtos.append(img_data.imagem)
                    if len(imagens_produtos) >= 4:
                        break

                # Buscar as cores associadas ao produto
                cores_produto = conn.execute(produto_cores.select().where(produto_cores.c.produto_id == item.id)).fetchall()
                cores_produtos = []
                for cor in cores_produto:
                    cor_data = conn.execute(cores.select().where(cores.c.id == cor.cores_id)).fetchone()
                    cores_produtos.append({'nome': cor_data.nome, 'hexadecimal': cor_data.hexadecimal})

                # Buscar o armazenamento associado ao produto
                armazenamento_produto = conn.execute(produto_armazenamento.select().where(produto_armazenamento.c.produto_id == item.id)).fetchall()
                armazenamento_produtos = []
                for arm in armazenamento_produto:
                    arm_data = conn.execute(armazenamento.select().where(armazenamento.c.id == arm.armazenamento_id)).fetchone()
                    armazenamento_produtos.append(arm_data.quantidade)

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
                    'armazenamento': armazenamento_produtos,
                    'categoria': item.categoria
                })

            return {'status': 200, 'produtos': produtos}
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            return {'status': 500, 'message': 'Erro ao listar produtos'}



# listar produtos por id
@produto_router.get("/lista-id/{id}")
async def listar_produto_id(id: int):
    with engine.connect() as conn:
        try:
            resultado = conn.execute(produto.select().where(produto.c.id == id)).fetchone()
            if resultado:
                imagens_produto = conn.execute(produto_imagens.select().where(produto_imagens.c.produto_id == resultado.id)).fetchall()
                imagens_produtos = []
                for img in imagens_produto:
                    img_data = conn.execute(imagens.select().where(imagens.c.id == img.imagens_id)).fetchone()
                    imagens_produtos.append(img_data.imagem)
                    if len(imagens_produtos) >= 4:
                        break

                cores_produto = conn.execute(produto_cores.select().where(produto_cores.c.produto_id == resultado.id)).fetchall()
                cores_produtos = []
                for cor in cores_produto:
                    cor_data = conn.execute(cores.select().where(cores.c.id == cor.cores_id)).fetchone()
                    cores_produtos.append({'nome': cor_data.nome, 'hexadecimal': cor_data.hexadecimal})

                armazenamento_produto = conn.execute(produto_armazenamento.select().where(produto_armazenamento.c.produto_id == resultado.id)).fetchall()
                armazenamento_produtos = []
                for arm in armazenamento_produto:
                    arm_data = conn.execute(armazenamento.select().where(armazenamento.c.id == arm.armazenamento_id)).fetchone()
                    armazenamento_produtos.append(arm_data.quantidade)

                produto_info = {
                    'id': resultado.id,
                    'nome': resultado.nome,
                    'desconto': resultado.desconto,
                    'preco': resultado.preco,
                    'descricao': resultado.descricao,
                    'data_cadastro': resultado.data_cadastro,
                    'ativo': resultado.ativo,
                    'miniatura': resultado.miniatura,
                    'imagens': imagens_produtos,
                    'cores': cores_produtos,
                    'armazenamento': armazenamento_produtos,
                    'categoria': resultado.categoria,
                    'estado': resultado.estado,
                    'formaEnvio': resultado.formaEnvio
                }
                return {'status': 200, 'produto': produto_info}
            else:
                return {'status': 404, 'message': 'Produto não encontrado'}
        except Exception as e:
            print(f"Erro ao listar produto: {e}")
            return {'status': 500, 'message': 'Erro ao listar produto'}


# listar produtos por categoria
@produto_router.get("/lista-categoria/{categoria}/{estado}")
async def listar_produto_categoria(categoria: str, estado: str):
    with engine.connect() as conn:
        try:
            result = conn.execute(produto.select().where(produto.c.categoria == categoria)).fetchall()
            produtos = []

            for item in result:
                imagens_produto = conn.execute(produto_imagens.select().where(produto_imagens.c.produto_id == item.id)).fetchall()
                imagens_produtos = []
                for img in imagens_produto:
                    img_data = conn.execute(imagens.select().where(imagens.c.id == img.imagens_id)).fetchone()
                    imagens_produtos.append(img_data.imagem)
                    if len(imagens_produtos) >= 4:
                        break

                cores_produto = conn.execute(produto_cores.select().where(produto_cores.c.produto_id == item.id)).fetchall()
                cores_produtos = []
                for cor in cores_produto:
                    cor_data = conn.execute(cores.select().where(cores.c.id == cor.cores_id)).fetchone()
                    cores_produtos.append({'nome': cor_data.nome, 'hexadecimal': cor_data.hexadecimal})

                armazenamento_produto = conn.execute(produto_armazenamento.select().where(produto_armazenamento.c.produto_id == item.id)).fetchall()
                armazenamento_produtos = []
                for arm in armazenamento_produto:
                    arm_data = conn.execute(armazenamento.select().where(armazenamento.c.id == arm.armazenamento_id)).fetchone()
                    armazenamento_produtos.append(arm_data.quantidade)

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
                    'armazenamento': armazenamento_produtos,
                    'categoria': item.categoria,
                    'estado': item.estado
                })

            return {'status': 200, 'produtos': produtos}
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            return {'status': 500, 'message': 'Erro ao listar produtos'}
        
# lista os produtos por categoria e estado
@produto_router.get("/lista-categoria-estado/{categoria}/{estado}")
async def listar_produto_categoria_estado(categoria: str, estado: str):
    with engine.connect() as conn:
        try:
            result = conn.execute(produto.select().where(produto.c.categoria == categoria, produto.c.estado == estado)).fetchall()
            produtos = []

            for item in result:
                imagens_produto = conn.execute(produto_imagens.select().where(produto_imagens.c.produto_id == item.id)).fetchall()
                imagens_produtos = []
                for img in imagens_produto:
                    img_data = conn.execute(imagens.select().where(imagens.c.id == img.imagens_id)).fetchone()
                    imagens_produtos.append(img_data.imagem)
                    if len(imagens_produtos) >= 4:
                        break

                cores_produto = conn.execute(produto_cores.select().where(produto_cores.c.produto_id == item.id)).fetchall()
                cores_produtos = []
                for cor in cores_produto:
                    cor_data = conn.execute(cores.select().where(cores.c.id == cor.cores_id)).fetchone()
                    cores_produtos.append({'nome': cor_data.nome, 'hexadecimal': cor_data.hexadecimal})

                armazenamento_produto = conn.execute(produto_armazenamento.select().where(produto_armazenamento.c.produto_id == item.id)).fetchall()
                armazenamento_produtos = []
                for arm in armazenamento_produto:
                    arm_data = conn.execute(armazenamento.select().where(armazenamento.c.id == arm.armazenamento_id)).fetchone()
                    armazenamento_produtos.append(arm_data.quantidade)

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
                    'armazenamento': armazenamento_produtos,
                    'categoria': item.categoria,
                    'estado': item.estado
                })

            return {'status': 200, 'produtos': produtos}
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            return {'status': 500, 'message': 'Erro ao listar produtos'}

# retorna todas as categorias cadastradas
@produto_router.get("/categorias")
async def listar_categorias():
    with engine.connect() as conn:
        try:
            result = conn.execute(produto.select()).fetchall()
            categorias = {}

            for item in result:
                # Adiciona a categoria ao dicionário se ainda não existir
                if item.categoria not in categorias:
                    categorias[item.categoria] = []
                # Adiciona o nome do produto à lista de produtos da categoria
                categorias[item.categoria].append({'id': item.id, 'nome':item.nome})

            return {'status': 200, 'categorias': categorias}
        except Exception as e:
            print(f"Erro ao listar categorias: {e}")
            return {'status': 500, 'message': 'Erro ao listar categorias'}
        

# pegar um produto de cada categoria para exibir na home, menos iphone
@produto_router.get("/destaques")
async def listar_destaque():
    with engine.connect() as conn:
        try:
            result = conn.execute(produto.select()).fetchall()
            produtos = []

            # verificar se não é iphone e se ja nao tem um produto da categoria na lista
            categorias = []
            for item in result:
                if item.categoria not in categorias and item.categoria != 'iphone':
                    categorias.append(item.categoria)
                    imagens_produto = conn.execute(produto_imagens.select().where(produto_imagens.c.produto_id == item.id)).fetchall()
                    imagens_produtos = []
                    for img in imagens_produto:
                        img_data = conn.execute(imagens.select().where(imagens.c.id == img.imagens_id)).fetchone()
                        imagens_produtos.append(img_data.imagem)
                        if len(imagens_produtos) >= 4:
                            break

                    cores_produto = conn.execute(produto_cores.select().where(produto_cores.c.produto_id == item.id)).fetchall()
                    cores_produtos = []
                    for cor in cores_produto:
                        cor_data = conn.execute(cores.select().where(cores.c.id == cor.cores_id)).fetchone()
                        cores_produtos.append({'nome': cor_data.nome, 'hexadecimal': cor_data.hexadecimal})

                    armazenamento_produto = conn.execute(produto_armazenamento.select().where(produto_armazenamento.c.produto_id == item.id)).fetchall()
                    armazenamento_produtos = []
                    for arm in armazenamento_produto:
                        arm_data = conn.execute(armazenamento.select().where(armazenamento.c.id == arm.armazenamento_id)).fetchone()
                        armazenamento_produtos.append(arm_data.quantidade)

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
                        'armazenamento': armazenamento_produtos,
                        'categoria': item.categoria
                    })

            return {'status': 200, 'produtos': produtos}
        except Exception as e:
            print(f"Erro ao listar destaques: {e}")
            return {'status': 500, 'message': 'Erro ao listar destaques'}
        


# pegar um produto de cada categoria para exibir na home, menos iphone
@produto_router.get("/destaques-exeto-produto/{id}")
async def listar_destaque_exeto_produto(id: int):
    with engine.connect() as conn:
        try:
            result = conn.execute(produto.select()).fetchall()
            produtos = []

            # verificar se não é iphone e se ja nao tem um produto da categoria na lista
            categorias = []
            for item in result:
                if item.categoria not in categorias and item.categoria != 'iphone' and item.id != id:
                    categorias.append(item.categoria)
                    imagens_produto = conn.execute(produto_imagens.select().where(produto_imagens.c.produto_id == item.id)).fetchall()
                    imagens_produtos = []
                    for img in imagens_produto:
                        img_data = conn.execute(imagens.select().where(imagens.c.id == img.imagens_id)).fetchone()
                        imagens_produtos.append(img_data.imagem)
                        if len(imagens_produtos) >= 4:
                            break

                    cores_produto = conn.execute(produto_cores.select().where(produto_cores.c.produto_id == item.id)).fetchall()
                    cores_produtos = []
                    for cor in cores_produto:
                        cor_data = conn.execute(cores.select().where(cores.c.id == cor.cores_id)).fetchone()
                        cores_produtos.append({'nome': cor_data.nome, 'hexadecimal': cor_data.hexadecimal})

                    armazenamento_produto = conn.execute(produto_armazenamento.select().where(produto_armazenamento.c.produto_id == item.id)).fetchall()
                    armazenamento_produtos = []
                    for arm in armazenamento_produto:
                        arm_data = conn.execute(armazenamento.select().where(armazenamento.c.id == arm.armazenamento_id)).fetchone()
                        armazenamento_produtos.append(arm_data.quantidade)

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
                        'armazenamento': armazenamento_produtos,
                        'categoria': item.categoria
                    })

            return {'status': 200, 'produtos': produtos}
        except Exception as e:
            print(f"Erro ao listar destaques: {e}")
            return {'status': 500, 'message': 'Erro ao listar destaques'}