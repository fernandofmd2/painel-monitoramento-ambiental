import streamlit as st
from app.ftp_handler import download_latest_file
from app.parser import parse_lsi_file
from app.style import set_style
from app.alarm_config import load_limits, save_limits
import time
from datetime import datetime, timedelta
import pytz

# Configuração da página
st.set_page_config(layout="wide")
set_style()

# Título fixo
st.markdown("<div class='title'>🌍 Painel de Monitoramento Ambiental</div>", unsafe_allow_html=True)
st.markdown("<div class='title-spacer'></div>", unsafe_allow_html=True)

# Ocultar menu padrão do Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Inicialização da sessão
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

if "alarm_limits" not in st.session_state:
    st.session_state.alarm_limits = load_limits()

if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# Cabeçalho com menu, título e botão atualizar
menu_col, spacer_col, update_col = st.columns([1, 5, 1])

with menu_col:
    if st.button("☰"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

with update_col:
    if st.button("🔄 Atualizar agora"):
        st.session_state.last_refresh_time = time.time()
        st.rerun()

# Última atualização (com fuso horário Brasil)
tz = pytz.timezone("America/Sao_Paulo")
local_time = datetime.fromtimestamp(st.session_state.last_refresh_time, tz)
dt_str = local_time.strftime("%d/%m/%Y %H:%M:%S")
st.markdown(f"📅 <b>Última atualização:</b> {dt_str}", unsafe_allow_html=True)

# Sidebar de alarmes
if st.session_state.show_sidebar:
    st.sidebar.header("⚙️ Configurar Alarmes")
    limits = st.session_state.alarm_limits

    for station_name in limits.keys():
        st.sidebar.subheader(f"Estação {station_name}")
        for param in limits[station_name]:
            limits[station_name][param]["min"] = st.sidebar.number_input(
                f"{station_name} - {param} (mínimo)", 
                value=limits[station_name][param]["min"]
            )
            limits[station_name][param]["max"] = st.sidebar.number_input(
                f"{station_name} - {param} (máximo)", 
                value=limits[station_name][param]["max"]
            )

    if st.sidebar.button("Salvar Configurações"):
        save_limits(limits)
        st.sidebar.success("Configurações salvas!")
        st.session_state.alarm_limits = limits

limits = st.session_state.alarm_limits

# Função para carregar dados da estação
def load_station_data(station_key):
    path, filename = download_latest_file(station_key)
    if not path:
        return {}, "", ""
    data = parse_lsi_file(path, station_key)
    timestamp = filename.replace("..lsi", "").replace("_", " ", 1).replace("_", ":", 1)
    return data, filename, timestamp

# Listas de parâmetros
gases_particulas = ["O3", "CO", "SO2", "NO", "NO2", "NOX", "PM10"]
meteorologicos = ["Temperatura", "Umidade Relativa", "Pressão Atmosférica",
                  "Direção do vento", "Velocidade do vento", "Índice Pluviométrico"]

col1, col_div, col2 = st.columns([1, 0.02, 1])

# Função para renderizar os dados ou alerta
def render_station(station_key, emoji, name, col):
    with col:
        data, filename, timestamp_str = load_station_data(station_key)

        # Se não há dados ou timestamp
        if not data or not timestamp_str:
            st.markdown(
                f"<div class='alert-card'>Sem novos dados da estação {name}</div>",
                unsafe_allow_html=True
            )
            return

        # Tenta converter timestamp do nome do arquivo
        try:
            # Formato esperado do arquivo: 17_07_2025 14_11
            ts_clean = timestamp_str.replace("..lsi", "").replace("_", " ")
            timestamp = datetime.strptime(ts_clean, "%d %m %Y %H %M")

            # Ajusta para fuso horário SP
            tz = pytz.timezone("America/Sao_Paulo")
            timestamp = tz.localize(timestamp)
        except Exception:
            st.markdown(
                f"<div class='alert-card'>Sem novos dados da estação {name}</div>",
                unsafe_allow_html=True
            )
            return

        # Verifica se o último dado está atrasado
        now = datetime.now(pytz.timezone("America/Sao_Paulo"))
        if now - timestamp > timedelta(minutes=30):
            st.markdown(
                f"<div class='alert-card'>Sem novos dados da estação {name} (último às {timestamp.strftime('%H:%M')})</div>",
                unsafe_allow_html=True
            )
            return

        # Se está dentro do tempo, mostra normalmente
        st.markdown(
            f"<p style='color:white; font-size:13px; text-align:center;'>📄 {filename}<br>🕒 {timestamp.strftime('%d/%m/%Y %H:%M')}</p>", 
            unsafe_allow_html=True
        )
        st.markdown(f"<div class='station-title'>{emoji} {name}</div>", unsafe_allow_html=True)

        col_gas, col_met = st.columns(2)

        with col_gas:
            st.subheader("Gases e Partículas")
            for label in gases_particulas:
                if label in data:
                    value = data[label]
                    alert = limits.get(name, {}).get(label, {})
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
                    alert = limits.get(name, {}).get(label, {})
                    min_val = alert.get("min", -1e9)
                    max_val = alert.get("max", 1e9)
                    alert_class = "alerta" if value < min_val or value > max_val else "normal"
                    st.markdown(f"""
                        <div class="metric-box {alert_class}">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{value:.3f}</div>
                        </div>
                    """, unsafe_allow_html=True)

# Render das estações
render_station("fazenda", "🏡", "Fazenda", col1)
with col_div:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
render_station("coca_cola", "🏭", "Coca Cola", col2)
