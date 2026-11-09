from fastapi import (FastAPI, HTTPException, Query, status)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from threading import Lock
import sys
import asyncio

lock_vendas = Lock()

# Modelo para validar os dados recebidos no POST
class ItemVenda(BaseModel):
    item: str = Field(min_length=1)
    preco_unitario: float = Field(gt=0)
    quantidade: int = Field(gt=0)

# Força o Windows a usar o Selector Event Loop, que não gera o erro 10054
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

# Permite que a GUI acesse os endpoints da API livremente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vendas = {
    1: {'item': 'lata', 'preco_unitario': 4, 'quantidade': 5},
    2: {'item': 'garrafa 2L', 'preco_unitario': 15, 'quantidade': 6},
    3: {'item': 'garrafa 600 ml', 'preco_unitario': 10, 'quantidade': 7},
    4: {'item': 'lata mini', 'preco_unitario': 2, 'quantidade': 8},
}

@app.get('/')
def home():
    return {'mensagem': 'API está no ar!'}


@app.get('/vendas/qtd-vendas')
def qtd_vendas():
    return {'quantidade_total': len(vendas)}


@app.get('/vendas/faturamento')
def calcular_faturamento():
    total = sum(v['preco_unitario'] * v['quantidade'] for v in vendas.values())

    return {
        "faturamento_total": round(total, 2),
        "moeda": "R$"
    }


@app.post('/vendas', status_code=201)
def criar_venda(venda: ItemVenda):
    with lock_vendas:
        # Gera um novo ID baseado no maior ID existente + 1
        novo_id = max(vendas.keys()) + 1 if vendas else 1

        # Salva no dicionário mantendo a estrutura original
        vendas[novo_id] = {
            'item': venda.item,
            'preco_unitario': venda.preco_unitario,
            'quantidade': venda.quantidade
        }

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,  # <-- Status técnico correto (201 Criado)
        content={
            "mensagem": "Venda cadastrada com sucesso no servidor!",
            "id_gerado": novo_id,
            "dados_salvos": vendas[novo_id]  # <-- Mostra ao aluno exatamente o que foi guardado
        }
    )


# Exemplo de uso: /vendas/busca?nome=lata&min_qtd=6
@app.get('/vendas/busca')
def buscar_vendas(
        nome: Optional[str] = Query(None, description="Parte do nome do item"),
        min_qtd: Optional[int] = Query(None, ge=0, description="Quantidade mínima vendida")
):
    resultados = {}
    for id_venda, dados in vendas.items():
        # Filtro por nome (ignora maiúsculas/minúsculas)
        if nome and nome.lower() not in dados['item'].lower():
            continue

        # Filtro por quantidade mínima
        if min_qtd is not None and dados['quantidade'] < min_qtd:
            continue

        resultados[id_venda] = dados

    return resultados


@app.get('/vendas/{id_venda}')
def get_venda(id_venda: int):
    # Busca a venda pelo ID. Se não existir, retorna erro 404.
    if id_venda not in vendas:
        raise HTTPException(status_code=404, detail="Venda não encontrada")

    return vendas[id_venda]


@app.put('/vendas/{id_venda}')
def atualizar_venda(id_venda: int, venda_atualizada: ItemVenda):
    novos_dados = {
        'item': venda_atualizada.item,
        'preco_unitario': venda_atualizada.preco_unitario,
        'quantidade': venda_atualizada.quantidade
    }

    with lock_vendas:
        if id_venda not in vendas:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venda não encontrada para atualização"
            )

        vendas[id_venda] = novos_dados.copy()

    return {
        "mensagem": f"Venda {id_venda} atualizada com sucesso.",
        "id": id_venda,
        "dados": novos_dados
    }


@app.delete('/vendas/{id_venda}')
def excluir_venda(id_venda: int):
    with lock_vendas:
        if id_venda not in vendas:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venda não encontrada para exclusão"
            )

        del vendas[id_venda]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "mensagem": (
                f"Venda {id_venda} deletada com sucesso. "
                "O registro foi removido do servidor."
            )
        }
    )

@app.get('/vendas')
def listar_vendas():
    return vendas