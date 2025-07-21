import streamlit as st
from app.ftp_handler import download_latest_file
from app.parser import parse_lsi_file
from app.style import set_style
from app.alarm_config import load_limits, save_limits
import time
from datetime import datetime
import pytz

st.set_page_config(layout="wide")
set_style()

# TÍTULO FIXO + espaçador
st.markdown("<div class='title'>Painel de Monitoramento Ambiental</div>", unsafe_allow_html=True)
st.markdown("<div class='title-spacer'></div>", unsafe_allow_html=True)

# Ocultar menu/rodapé padrão
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Sessão inicial
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

# Controle de refresh
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# Auto-refresh a cada 5 min
if time.time() - st.session_state.last_refresh_time >= 300:
    st.session_state.last_refresh_time = time.time()
    st.rerun()

# Cabeçalho
menu_col, spacer_col, update_col = st.columns([1, 5, 1])
with menu_col:
    if st.button("☰"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

with update_col:
    if st.button("🔄 Atualizar agora"):
        st.session_state.last_refresh_time = time.time()
        st.rerun()

# Última atualização formatada
tz = pytz.timezone("America/Sao_Paulo")
local_time = datetime.fromtimestamp(st.session_state.last_refresh_time, tz)
dt_str = local_time.strftime("%d/%m/%Y %H:%M:%S")
st.markdown(f"📅 <b>Última atualização:</b> {dt_str}", unsafe_allow_html=True)

# Lista de estações para limites separados
STATIONS = {
    "fazenda": "Estação Bom Retiro",
    "coca_cola": "Estação Porto Real"
}

# Sidebar
if st.session_state.show_sidebar:
    st.sidebar.header("⚙️ Configurar Alarmes")

    selected_station_key = st.sidebar.selectbox(
        "Selecione a estação para configurar limites",
        options=list(STATIONS.keys()),
        format_func=lambda k: STATIONS[k]
    )

    # Carrega os limites específicos dessa estação
    if selected_station_key not in st.session_state:
        st.session_state[selected_station_key] = load_limits(selected_station_key)

    current_limits = st.session_state[selected_station_key]

    st.sidebar.markdown(f"### {STATIONS[selected_station_key]}")

    for param in current_limits:
        st.sidebar.subheader(param)
        current_limits[param]["min"] = st.sidebar.number_input(
            f"{param} - mínimo",
            value=current_limits[param]["min"],
            key=f"{selected_station_key}_{param}_min"
        )
        current_limits[param]["max"] = st.sidebar.number_input(
            f"{param} - máximo",
            value=current_limits[param]["max"],
            key=f"{selected_station_key}_{param}_max"
        )

    if st.sidebar.button("💾 Salvar Configurações"):
        save_limits(current_limits, selected_station_key)
        st.sidebar.success(f"Configurações salvas para {STATIONS[selected_station_key]}!")
        st.session_state[selected_station_key] = current_limits

# Função FTP
def load_station_data(station_key):
    path, filename = download_latest_file(station_key)
    if not path:
        return {}, "", ""
    data = parse_lsi_file(path, station_key)
    timestamp = filename.replace(".lsi", "").replace("_", "/", 1).replace("_", ":", 1)
    return data, filename, timestamp

# Parâmetros
gases_particulas = ["O3", "CO", "SO2", "NO", "NO2", "NOX", "PM10"]
meteorologicos = [
    "Temperatura", "Umidade Relativa", "Pressão Atmosférica",
    "Direção do vento", "Velocidade do vento", "Índice Pluviométrico"
]

col1, col_div, col2 = st.columns([1, 0.02, 1])

def render_station(station_key, emoji, name, col):
    with col:
        data, filename, timestamp = load_station_data(station_key)
        if not data:
            st.warning(f"Sem dados da {name}")
            return

        st.markdown(f"<p style='color:white; font-size:13px; text-align:center;'>📄 {filename}<br>🕒 {timestamp}</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='station-title'>{emoji} {name}</div>", unsafe_allow_html=True)

        # Carrega limites corretos da estação
        station_limits = st.session_state.get(station_key, load_limits(station_key))

        col_gas, col_met = st.columns(2)

        with col_gas:
            st.subheader("Gases e Partículas")
            for label in gases_particulas:
                if label in data:
                    value = data[label]
                    alert = station_limits.get(label, {})
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
                    alert = station_limits.get(label, {})
                    min_val = alert.get("min", -1e9)
                    max_val = alert.get("max", 1e9)
                    alert_class = "alerta" if value < min_val or value > max_val else "normal"
                    st.markdown(f"""
                        <div class="metric-box {alert_class}">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{value:.3f}</div>
                        </div>
                    """, unsafe_allow_html=True)

render_station("fazenda", "", "Estação Bom Retiro", col1)
with col_div:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
render_station("coca_cola", "", "Estação Porto Real", col2)
