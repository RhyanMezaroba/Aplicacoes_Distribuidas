import sys
import asyncio
import time

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"
TIMEOUT = 5

st.set_page_config(
    page_title="Gerenciador de Vendas",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 0.8rem;
    }

    h1 {
        font-size: 1.75rem !important;
        margin-top: 0 !important;
        margin-bottom: 0.4rem !important;
    }

    h2, h3 {
        font-size: 1.25rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.35rem !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.45rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Painel Gerenciador de Vendas")

def carregar_resumo():
    response = requests.get(f"{API_URL}/", timeout=TIMEOUT)
    response.raise_for_status()
    status_api = response.json()

    response = requests.get(f"{API_URL}/vendas/faturamento", timeout=TIMEOUT)
    response.raise_for_status()
    faturamento = response.json()

    response = requests.get(f"{API_URL}/vendas/qtd-vendas", timeout=TIMEOUT)
    response.raise_for_status()
    quantidade = response.json()

    return status_api, faturamento, quantidade


def limpar_formulario_edicao():
    st.session_state.id_carregado_formulario = None

    for chave in ("edit_nome", "edit_preco", "edit_qtd"):
        st.session_state.pop(chave, None)


try:
    res_status, res_fat, res_qtd = carregar_resumo()

    st.sidebar.header("⚙️ Resumo do Sistema")
    st.sidebar.success(f"API: {res_status['mensagem']}")
    st.sidebar.metric("Faturamento Total", f"{res_fat['moeda']} " f"{res_fat['faturamento_total']:.2f}")
    st.sidebar.metric("Total de Vendas", res_qtd["quantidade_total"])
except requests.exceptions.ConnectionError:
    st.error("❌ Não foi possível conectar à API FastAPI.")
    st.stop()
except requests.exceptions.Timeout:
    st.error("❌ A API demorou muito para responder.")
    st.stop()
except requests.exceptions.RequestException as erro:
    st.error(f"❌ Erro de comunicação com a API: {erro}")
    st.stop()

st.markdown("### 🔍 Vendas Cadastradas")
col_nome, col_qtd = st.columns([3, 1])

with col_nome:
    busca_nome = st.text_input(
        "Filtrar por nome",
        label_visibility="collapsed",
        placeholder="🔎 Filtrar por nome do item"
    )

with col_qtd:
    busca_qtd = st.number_input(
        "Quantidade mínima",
        min_value=0,
        value=0,
        step=1,
        label_visibility="collapsed"
    )

params = {}

if busca_nome:
    params["nome"] = busca_nome

if busca_qtd > 0:
    params["min_qtd"] = busca_qtd

try:
    response = requests.get(
        f"{API_URL}/vendas/busca",
        params=params,
        timeout=TIMEOUT
    )

    response.raise_for_status()
    dados_vendas = response.json()
except requests.exceptions.RequestException as erro:
    st.error(f"Erro ao consultar as vendas: {erro}")
    dados_vendas = {}

if dados_vendas:
    dados_lista = []

    for id_venda, dados in dados_vendas.items():
        preco = float(dados["preco_unitario"])
        quantidade = int(dados["quantidade"])

        dados_lista.append({
            "ID": int(id_venda),
            "Item": dados["item"],
            "Preço Unit. (R$)": preco,
            "Qtd.": quantidade,
            "Total (R$)": preco * quantidade
        })

    df = pd.DataFrame(dados_lista)

    ids_tabela = "_".join(
        str(id_venda)
        for id_venda in df["ID"].tolist()
    )

    chave_tabela = (f"tabela_vendas_{ids_tabela}")

    evento = st.dataframe(
        df,
        key=chave_tabela,
        width="stretch",
        height=210,
        row_height=32,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-cell",
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Item": st.column_config.TextColumn("Item", width="large"),
            "Preço Unit. (R$)": st.column_config.NumberColumn("Preço Unit. (R$)", format="R$ %.2f"),
            "Qtd.": st.column_config.NumberColumn("Qtd.", width="small"),
            "Total (R$)": st.column_config.NumberColumn("Total (R$)", format="R$ %.2f")
        }
    )

    celulas = evento.selection.cells

    if celulas:
        indice_linha = celulas[0][0]

        if 0 <= indice_linha < len(df):
            id_clicado = int(df.iloc[indice_linha]["ID"])

            if (st.session_state.get("id_selecionado") != id_clicado):
                st.session_state.id_selecionado = (id_clicado)
else:
    st.warning("Nenhum registro encontrado.")
    st.session_state.id_selecionado = None

id_selecionado = st.session_state.get("id_selecionado")

if id_selecionado is not None:
    try:
        response = requests.get(f"{API_URL}/vendas/{id_selecionado}", timeout=TIMEOUT)
        response.raise_for_status()
        dados_atuais = response.json()
    except requests.exceptions.RequestException as erro:
        st.error(f"Erro ao carregar a venda: {erro}")
        dados_atuais = None

    if dados_atuais:
        if (st.session_state.get("id_carregado_formulario") != id_selecionado):
            st.session_state.id_carregado_formulario = (id_selecionado)
            st.session_state.edit_nome = (dados_atuais["item"])
            st.session_state.edit_preco = float(dados_atuais["preco_unitario"])
            st.session_state.edit_qtd = int(dados_atuais["quantidade"])

        st.markdown(f"### ✏️ Alterar Venda — ID {id_selecionado}")

        with st.form("form_edicao"):
            (col_item, col_preco, col_qtd, col_salvar, col_excluir) = st.columns([3, 1.3, 1, 1.15, 1.15])

            with col_item:
                novo_item = st.text_input("Item", key="edit_nome" )

            with col_preco:
                novo_preco = st.number_input(
                    "Preço (R$)",
                    min_value=0.01,
                    step=1.0,
                    format="%.2f",
                    key="edit_preco"
                )

            with col_qtd:
                nova_qtd = st.number_input(
                    "Quantidade",
                    min_value=1,
                    step=1,
                    key="edit_qtd"
                )

            with col_salvar:
                st.write("")
                st.write("")

                salvar = st.form_submit_button("💾 Salvar", type="primary", width="stretch")

            with col_excluir:
                st.write("")
                st.write("")

                excluir = st.form_submit_button("🗑️ Excluir", width="stretch")

        if salvar:
            if not novo_item.strip():
                st.error("O nome do item não pode ficar vazio.")
            else:
                payload = {
                    "item": novo_item.strip(),
                    "preco_unitario": novo_preco,
                    "quantidade": nova_qtd
                }

                try:
                    response = requests.put(
                        f"{API_URL}/vendas/{id_selecionado}",
                        json=payload,
                        timeout=TIMEOUT
                    )

                    if response.status_code == 200:
                        resposta = response.json()

                        st.success(
                            resposta.get("mensagem", "Venda atualizada com sucesso.")
                        )

                        limpar_formulario_edicao()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(
                            f"Erro {response.status_code}: "
                            f"{response.text}"
                        )

                except requests.exceptions.Timeout:
                    st.error("A API demorou muito para responder.")
                except requests.exceptions.RequestException as erro:
                    st.error(f"Erro de comunicação: {erro}")

        if excluir:
            try:
                response = requests.delete(f"{API_URL}/vendas/{id_selecionado}", timeout=TIMEOUT)

                if response.status_code == 200:
                    resposta = response.json()

                    st.success(
                        resposta.get(
                            "mensagem",
                            "Venda excluída com sucesso."
                        )
                    )

                    st.session_state.id_selecionado = None

                    limpar_formulario_edicao()
                    time.sleep(3)
                    st.rerun()
                else:
                    st.error(
                        f"Erro {response.status_code}: "
                        f"{response.text}"
                    )
            except requests.exceptions.Timeout:
                st.error("A API demorou muito para responder.")
            except requests.exceptions.RequestException as erro:
                st.error(f"Erro de comunicação: {erro}")
else:
    st.caption(
        "Selecione uma venda na tabela "
        "para editar ou excluir."
    )


st.markdown("### ➕ Nova Venda")

with st.form("form_cadastro", clear_on_submit=True):
    (col_item, col_preco, col_qtd, col_botao) = st.columns([3, 1.3, 1, 1.5])

    with col_item:
        item = st.text_input("Nome do Item")

    with col_preco:
        preco = st.number_input(
            "Preço Unitário (R$)",
            min_value=0.01,
            value=1.00,
            step=1.0,
            format="%.2f"
        )

    with col_qtd:
        quantidade = st.number_input(
            "Quantidade",
            min_value=1,
            value=1,
            step=1
        )

    with col_botao:
        st.write("")
        st.write("")

        cadastrar = (
            st.form_submit_button(
                "➕ Cadastrar",
                type="primary",
                width="stretch"
            )
        )

    if cadastrar:
        if not item.strip():
            st.error("O nome do item não pode ficar vazio.")
        else:
            payload = {
                "item": item.strip(),
                "preco_unitario": preco,
                "quantidade": quantidade
            }

            try:
                response = requests.post(
                    f"{API_URL}/vendas",
                    json=payload,
                    timeout=TIMEOUT
                )

                if response.status_code == 201:
                    resposta = response.json()

                    st.success(
                        resposta.get("mensagem", "Venda cadastrada com sucesso.")
                    )

                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(
                        f"Erro {response.status_code}: "
                        f"{response.text}"
                    )
            except requests.exceptions.Timeout:
                st.error("A API demorou muito para responder.")
            except requests.exceptions.RequestException as erro:
                st.error(f"Erro de comunicação: {erro}")