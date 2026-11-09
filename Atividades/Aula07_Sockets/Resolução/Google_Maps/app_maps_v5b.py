# app_maps_v5b.py
import os
import socket
import ssl
import json
from urllib.parse import quote_plus
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# 1. Carregamento seguro da chave a partir do arquivo .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(
    page_title="Google Maps com Streamlit",
    page_icon="📍",
    layout="wide"
)

st.title("📍 Painel de Geolocalização com Google Maps e Streamlit")

if not API_KEY:
    st.error("A variável GOOGLE_API_KEY não foi configurada no arquivo .env.")
    st.stop()

# 2. Função de Geocodificação com Cache para otimizar requisições
@st.cache_data(show_spinner=False)
def geocode_google(endereco):
    endereco_codificado = quote_plus(endereco)
    url = (
        "https://maps.googleapis.com/maps/api/geocode/json"
        f"?address={endereco_codificado}"
        f"&key={API_KEY}"
        "&language=pt-BR"
        "&region=br"
    )
    contexto_ssl = ssl.create_default_context()
    requisicao = Request(
        url,
        headers={
            "User-Agent": "StreamlitGoogleMaps/1.0",
            "Accept": "application/json"
        }
    )
    try:
        with urlopen(requisicao, timeout=10, context=contexto_ssl) as resposta:
            corpo = resposta.read().decode("utf-8")
    except HTTPError as erro:
        raise Exception(f"Erro HTTP ao acessar o Google: {erro.code}")
    except URLError as erro:
        raise Exception(f"Erro de conexão com o Google: {erro.reason}")
    except socket.timeout:
        raise Exception("Tempo limite excedido ao aguardar resposta do Google.")

    dados = json.loads(corpo)
    status = dados.get("status")

    if status == "ZERO_RESULTS":
        return None
    if status != "OK":
        mensagem = dados.get("error_message", "Erro não especificado.")
        raise Exception(f"Google Geocoding API: {status} - {mensagem}")

    resultado = dados["results"][0]
    coordenadas = resultado["geometry"]["location"]
    return {
        "latitude": coordenadas["lat"],
        "longitude": coordenadas["lng"],
        "endereco": resultado["formatted_address"],
        "place_id": resultado.get("place_id")
    }

# 3. Gerenciamento do estado da sessão (Session State)
if "endereco_atual" not in st.session_state:
    st.session_state.endereco_atual = "Rua Paese, 198, Videira, SC, Brasil"
if "latitude" not in st.session_state:
    st.session_state.latitude = -27.009400
if "longitude" not in st.session_state:
    st.session_state.longitude = -51.150100
if "place_id" not in st.session_state:
    st.session_state.place_id = None

# 4. Formulário para pesquisa sem re-renderização precoce
with st.form("formulario_pesquisa"):
    endereco_input = st.text_input(
        "Endereço para pesquisa:",
        value=st.session_state.endereco_atual
    )
    procurar = st.form_submit_button("🔎 Procurar")

if procurar:
    if not endereco_input.strip():
        st.warning("Por favor, digite um endereço para realizar a pesquisa.")
    else:
        try:
            with st.spinner("Consultando Google Geocoding API..."):
                local = geocode_google(endereco_input.strip())
            if local:
                st.session_state.latitude = local["latitude"]
                st.session_state.longitude = local["longitude"]
                st.session_state.endereco_atual = local["endereco"]
                st.session_state.place_id = local["place_id"]
            else:
                st.warning("Endereço não encontrado.")
        except Exception as erro:
            st.error(str(erro))

# 5. Exibição dos dados geodésicos formatados
st.subheader("Localização Encontrada")
col1, col2 = st.columns(2)
with col1:
    st.metric("Latitude", f"{st.session_state.latitude:.6f}")
with col2:
    st.metric("Longitude", f"{st.session_state.longitude:.6f}")

st.write("**Endereço Formatado Oficial:**", st.session_state.endereco_atual)

# 6. Incorporação oficial do Google Maps via Iframe
if st.session_state.place_id:
    consulta_mapa = quote_plus("place_id:" + st.session_state.place_id)
else:
    consulta_mapa = quote_plus(st.session_state.endereco_atual)

url_mapa = (
    "https://www.google.com/maps/embed/v1/place"
    f"?key={API_KEY}"
    f"&q={consulta_mapa}"
    "&language=pt-BR"
    "&region=BR"
)

st.iframe(url_mapa, height=600)
