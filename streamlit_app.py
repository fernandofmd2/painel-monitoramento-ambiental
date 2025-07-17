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

# === INICIALIZAÇÃO DA SESSÃO ===
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

if "alarm_limits" not in st.session_state:
    st.session_state.alarm_limits = load_limits()

if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# === CABEÇALHO ===
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

# === SIDEBAR PARA CONFIG ALARMES ===
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

# === FUNÇÃO PARA CARREGAR DADOS FTP ===
def load_station_data(station_key):
    path, filename = download_latest_file(station_key)
    if not path:
        return {}, "", None
    
    data = parse_lsi_file(path, station_key)
    
    timestamp = None
    try:
        # tenta converter nome do arquivo em datetime
        ts_clean = filename.replace("..lsi", "")
        parts = ts_clean.split("_")
        # Exemplo esperado: 17_07_2025_14_11
        if len(parts) >= 5:
            day, month, year, hour, minute = parts[:5]
            timestamp = datetime(int(year), int(month), int(day), int(hour), int(minute))
    except Exception:
        timestamp = None

    return data, filename, timestamp

# === LISTAS DE PARÂMETROS ===
gases_particulas = ["O3", "CO", "SO2", "NO", "NO2", "NOX", "PM10"]
meteorologicos = ["Temperatura", "Umidade Relativa", "Pressão Atmosférica",
                  "Direção do vento", "Velocidade do vento", "Índice Pluviométrico"]

col1, col_div, col2 = st.columns([1, 0.02, 1])

# === FUNÇÃO PARA RENDERIZAR ESTAÇÃO ===
def render_station(station_key, emoji, name, col):
    with col:
        data, filename, timestamp = load_station_data(station_key)

        # Se não conseguiu carregar nada
        if not data:
            st.warning(f"Sem dados da Estação {name}")
            return

        tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(tz)

        # Se timestamp está None ou inválido -> considera atrasado
        if not timestamp:
            st.markdown(f"<div class='station-title'>{emoji} {name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='alert-card'>Sem novos dados da estação {name}</div>", unsafe_allow_html=True)
            return

        # Se está atrasado >30 minutos
        try:
            if now - timestamp > timedelta(minutes=30):
                st.markdown(f"<div class='station-title'>{emoji} {name}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='alert-card'>Sem novos dados da estação {name} há mais de 30 minutos!</div>", unsafe_allow_html=True)
                return
        except Exception:
            st.markdown(f"<div class='station-title'>{emoji} {name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='alert-card'>Sem novos dados da estação {name}</div>", unsafe_allow_html=True)
            return

        # Se chegou aqui, está atualizado → mostra normalmente
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

# === RENDERIZA ESTAÇÕES ===
render_station("fazenda", "", "Fazenda", col1)
with col_div:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
render_station("coca_cola", "", "Coca Cola", col2)
