import streamlit as st
from app.ftp_handler import download_latest_file
from app.parser import parse_lsi_file
from app.style import set_style
from app.alarm_config import load_limits, save_limits
import time
from datetime import datetime, timedelta
import pytz

st.set_page_config(layout="wide")
set_style()

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .alert-card {
        background-color: #8B0000;
        color: white;
        text-align: center;
        font-size: 22px;
        padding: 30px;
        border-radius: 10px;
        font-weight: bold;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização de sessão
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

if "alarm_limits" not in st.session_state:
    st.session_state.alarm_limits = load_limits()

if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# Cabeçalho
menu_col, title_col, update_col = st.columns([1, 5, 1])

with menu_col:
    if st.button("☰"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

with title_col:
    st.markdown("<div class='title'>🌍 Painel de Monitoramento Ambiental</div>", unsafe_allow_html=True)

with update_col:
    if st.button("🔄 Atualizar agora"):
        st.session_state.last_refresh_time = time.time()
        st.rerun()

# Exibe última atualização (com fuso horário corrigido)
tz = pytz.timezone("America/Sao_Paulo")
local_time = datetime.fromtimestamp(st.session_state.last_refresh_time, tz)
dt_str = local_time.strftime("%d/%m/%Y %H:%M:%S")
st.markdown(f"📅 <b>Última atualização:</b> {dt_str}", unsafe_allow_html=True)

# Sidebar para limites
if st.session_state.show_sidebar:
    st.sidebar.header("⚙️ Configurar Alarmes")
    limits = st.session_state.alarm_limits

    for estacao, params in limits.items():
        st.sidebar.subheader(f"🚩 Limites para {estacao}")
        for param in params:
            params[param]["min"] = st.sidebar.number_input(
                f"{estacao} - {param} mínimo", value=params[param]["min"]
            )
            params[param]["max"] = st.sidebar.number_input(
                f"{estacao} - {param} máximo", value=params[param]["max"]
            )

    if st.sidebar.button("Salvar Configurações"):
        save_limits(limits)
        st.sidebar.success("Configurações salvas!")
        st.session_state.alarm_limits = limits

limits = st.session_state.alarm_limits

# Função para carregar dados do FTP
def load_station_data(station_key):
    path, filename = download_latest_file(station_key)
    if not path:
        return {}, "", "", None
    
    # Parse normal
    data = parse_lsi_file(path, station_key)
    
    # Converte timestamp do nome do arquivo
    try:
        timestamp = datetime.strptime(filename.split(".")[0], "%d_%m_%Y%H_%M")
    except:
        # fallback seguro
        timestamp = datetime.now() - timedelta(hours=1)

    return data, filename, timestamp

# Listas de parâmetros
gases_particulas = ["O3", "CO", "SO2", "NO", "NO2", "NOX", "PM10"]
meteorologicos = ["Temperatura", "Umidade Relativa", "Pressão Atmosférica",
                  "Direção do vento", "Velocidade do vento", "Índice Pluviométrico"]

col1, col_div, col2 = st.columns([1, 0.02, 1])

def render_station(station_key, emoji, name, col):
    with col:
        data, filename, timestamp = load_station_data(station_key)
        
        if not data:
            st.warning(f"Sem dados da Estação {name}")
            return
        
        # Tempo atual em SP
        tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(tz)
        
        # Se está atrasado >30 min, mostra ALERTA VERMELHO e não mostra dados
        if now - timestamp > timedelta(minutes=30):
            st.markdown(f"<div class='station-title'>{emoji} {name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='alert-card'>🚨 Sem novos dados da estação <b>{name}</b> há mais de 30 minutos!</div>", unsafe_allow_html=True)
            return
        
        # Caso esteja atualizado, renderiza normalmente
        st.markdown(f"<p style='color:white; font-size:13px; text-align:center;'>📄 {filename}<br>🕒 {timestamp.strftime('%d/%m/%Y %H:%M:%S')}</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='station-title'>{emoji} {name}</div>", unsafe_allow_html=True)

        col_gas, col_met = st.columns(2)

        est_limits = limits.get(name, {})

        with col_gas:
            st.subheader("Gases e Partículas")
            for label in gases_particulas:
                if label in data:
                    value = data[label]
                    alert = est_limits.get(label, {})
                    min_val = alert.get("min", -1e9)
                    max_val = alert.get("max", 1e9)
                    alert_class = "alerta" if value < min_val or value > max_val else "normal"
                    st.markdown(f"""
                        <div class="metric-box {alert_class}">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{value:.3f}</div>
                        </div>
                    """, unsafe_allow_html=True)

        with col_met:
            st.subheader("Variáveis Meteorológicas")
            for label in meteorologicos:
                if label in data:
                    value = data[label]
                    alert = est_limits.get(label, {})
                    min_val = alert.get("min", -1e9)
                    max_val = alert.get("max", 1e9)
                    alert_class = "alerta" if value < min_val or value > max_val else "normal"
                    st.markdown(f"""
                        <div class="metric-box {alert_class}">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{value:.3f}</div>
                        </div>
                    """, unsafe_allow_html=True)

# Render das estações normalmente
render_station("fazenda", "🏡", "Fazenda", col1)
with col_div:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
render_station("coca_cola", "🥤", "Coca Cola", col2)
