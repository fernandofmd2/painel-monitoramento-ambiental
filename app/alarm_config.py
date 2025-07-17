import json
import os

# Pasta onde ficam os arquivos de limites por estação
BASE_PATH = "data/limits"

# Valores padrão para todos os parâmetros
PARAMS_DEFAULTS = {
    "O3": {"min": 0.0, "max": 200.0},
    "CO": {"min": 0.0, "max": 200.0},
    "SO2": {"min": 0.0, "max": 200.0},
    "NO": {"min": 0.0, "max": 200.0},
    "NO2": {"min": 0.0, "max": 200.0},
    "NOX": {"min": 0.0, "max": 200.0},
    "PM10": {"min": 0.0, "max": 200.0},
    "Temperatura": {"min": -10.0, "max": 60.0},
    "Umidade Relativa": {"min": 0.0, "max": 100.0},
    "Pressão Atmosférica": {"min": 800.0, "max": 1100.0},
    "Direção do vento": {"min": 0.0, "max": 360.0},
    "Velocidade do vento": {"min": 0.0, "max": 50.0},
    "Índice Pluviométrico": {"min": 0.0, "max": 500.0},
}

def _get_station_file(station_key: str):
    """Retorna o caminho do arquivo de limites da estação"""
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH, exist_ok=True)
    return os.path.join(BASE_PATH, f"limits_{station_key}.json")

def load_limits(station_key: str):
    """Carrega os limites específicos de uma estação"""
    filepath = _get_station_file(station_key)
    if not os.path.exists(filepath):
        # Se não existe, cria com defaults
        save_limits(PARAMS_DEFAULTS, station_key)
        return PARAMS_DEFAULTS.copy()
    with open(filepath, "r") as f:
        return json.load(f)

def save_limits(limits, station_key: str):
    """Salva os limites específicos de uma estação"""
    filepath = _get_station_file(station_key)
    with open(filepath, "w") as f:
        json.dump(limits, f, indent=4)
