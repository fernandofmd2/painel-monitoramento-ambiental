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

# TÍTULO FIXO
st.markdown("<div class='title'>🌍 Painel de Monitoramento Ambiental</div>", unsafe_allow_html=True)

# Oculta menu padrão Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Inicialização de sessão
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

if "alarm_limits" not in st.session_state:
    st.session_state.alarm_limits = load_limits()

# Guarda o horário da última atualização (inicializa)
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# Cabeçalho com menu e botão atualizar
menu_col, spacer_col, update_col = st.columns([1, 5, 1])

with menu_col:
    if st.button("☰"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

with update_col:
    # Atualiza manualmente
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

    for param in limits:
        st.sidebar.subheader(param)
        limits[param]["min"] = st.sidebar.number_input(f"{param} - mínimo", value=limits[param]["min"])
        limits[param]["max"] = st.sidebar.number_input(f"{param} - máximo", value=limits[param]["max"])

    if st.sidebar.button("Salvar Configurações"):
        save_limits(limits)
        st.sidebar.success("Configurações salvas!")
        st.session_state.alarm_limits = limits

limits = st.session_state.alarm_limits

# Função que carrega dados do FTP
def load_station_data(station_key):
    path, filename = download_latest_file(station_key)
    if not path:
        return {}, "", ""
    data = parse_lsi_file(path, station_key)
    return data, filename

# Função para extrair horário do arquivo .lsi
def get_file_datetime(filename):
    try:
        # Exemplo: 17_07_2025_14_11..lsi
        parts = filename.replace("..lsi", "").split("_")
        day, month, year, hour, minute = parts
        dt = datetime(int(year), int(month), int(day), int(hour), int(minute))
        return dt
    except Exception:
        return None

# Variáveis
gases_particulas = ["O3", "CO", "SO2", "NO", "NO2", "NOX", "PM10"]
meteorologicos = ["Temperatura", "Umidade Relativa", "Pressão Atmosférica",
                  "Direção do vento", "Velocidade do vento", "Índice Pluviométrico"]

# Layout em duas colunas
col1, col_div, col2 = st.columns([1, 0.02, 1])

# Renderização por estação
def render_station(station_key, emoji, name, col):
    with col:
        data, filename = load_station_data(station_key)
        if not data:
            st.warning(f"Sem dados da Estação {name}")
            return

        # Verifica o horário do arquivo
        file_dt = get_file_datetime(filename)
        tz_br = pytz.timezone("America/Sao_Paulo")
        now_br = datetime.now(tz_br)
        delay_ok = False
        file_time_str = ""

        if file_dt:
            # Converte para timezone Brasil
            file_dt = tz_br.localize(file_dt)
            diff_minutes = (now_br - file_dt).total_seconds() / 60.0
            delay_ok = diff_minutes <= 30  # dentro do limite
            file_time_str = file_dt.strftime("%d/%m/%Y %H:%M")

        # Se o atraso é maior que 30min, mostra ALERTA VERMELHO
        if not delay_ok:
            last_seen = f"Último dado recebido: {file_time_str}" if file_time_str else "Último horário desconhecido"
            st.markdown(f"""
                <div style='background-color:#8B0000; color:white; padding:25px; text-align:center; border-radius:12px; font-size:20px;'>
                🚨 <b>Sem atualização da Estação {name} há mais de 30 minutos!</b><br><br>
                ⏳ {last_seen}
                </div>
            """, unsafe_allow_html=True)
            return

        # Exibe dados normalmente se está atualizado
        st.markdown(f"<p style='color:white; font-size:13px; text-align:center;'>📄 {filename} <br>🕒 {file_time_str}</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='station-title'>{emoji} {name}</div>", unsafe_allow_html=True)

        # Duas colunas: gases e meteorológicos
        col_gas, col_met = st.columns(2)

        with col_gas:
            st.subheader("Gases e Partículas")
            for label in gases_particulas:
                if label in data:
                    value = data[label]
                    alert = limits.get(label, {})
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
                    alert = limits.get(label, {})
                    min_val = alert.get("min", -1e9)
                    max_val = alert.get("max", 1e9)
                    alert_class = "alerta" if value < min_val or value > max_val else "normal"
                    st.markdown(f"""
                        <div class="metric-box {alert_class}">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{value:.3f}</div>
                        </div>
                    """, unsafe_allow_html=True)

# Render das estações (executa a cada atualização manual)
render_station("fazenda", "", "Fazenda", col1)
with col_div:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
render_station("coca_cola", "", "Coca Cola", col2)
