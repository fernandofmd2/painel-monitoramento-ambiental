import json
import os

# Pasta onde os limites ficam salvos
LIMITS_DIR = "limits"

# Nome do arquivo principal para salvar os limites
DEFAULT_LIMITS_FILE = os.path.join(LIMITS_DIR, "station_limits.json")

# Limites padrão para cada estação
DEFAULT_LIMITS = {
    "Fazenda": {
        "O3": {"min": 0.0, "max": 200.0},
        "CO": {"min": 0.0, "max": 50.0},
        "SO2": {"min": 0.0, "max": 20.0},
        "NO": {"min": 0.0, "max": 10.0},
        "NO2": {"min": 0.0, "max": 10.0},
        "NOX": {"min": 0.0, "max": 10.0},
        "PM10": {"min": 0.0, "max": 150.0},
        "Temperatura": {"min": -10.0, "max": 50.0},
        "Umidade Relativa": {"min": 0.0, "max": 100.0},
        "Pressão Atmosférica": {"min": 900.0, "max": 1100.0},
        "Direção do vento": {"min": 0.0, "max": 360.0},
        "Velocidade do vento": {"min": 0.0, "max": 50.0},
        "Índice Pluviométrico": {"min": 0.0, "max": 500.0}
    },
    "Coca Cola": {
        "O3": {"min": 0.0, "max": 200.0},
        "CO": {"min": 0.0, "max": 50.0},
        "SO2": {"min": 0.0, "max": 20.0},
        "NO": {"min": 0.0, "max": 10.0},
        "NO2": {"min": 0.0, "max": 10.0},
        "NOX": {"min": 0.0, "max": 10.0},
        "PM10": {"min": 0.0, "max": 150.0},
        "Temperatura": {"min": -10.0, "max": 50.0},
        "Umidade Relativa": {"min": 0.0, "max": 100.0},
        "Pressão Atmosférica": {"min": 900.0, "max": 1100.0},
        "Direção do vento": {"min": 0.0, "max": 360.0},
        "Velocidade do vento": {"min": 0.0, "max": 50.0},
        "Índice Pluviométrico": {"min": 0.0, "max": 500.0}
    }
}

def ensure_limits_dir():
    """Garante que a pasta limits existe"""
    if not os.path.exists(LIMITS_DIR):
        os.makedirs(LIMITS_DIR)

def load_limits():
    """Carrega os limites salvos ou cria o padrão se não existir"""
    ensure_limits_dir()
    if not os.path.exists(DEFAULT_LIMITS_FILE):
        save_limits(DEFAULT_LIMITS)
        return DEFAULT_LIMITS

    try:
        with open(DEFAULT_LIMITS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar limites: {e}")
        return DEFAULT_LIMITS

def save_limits(limits_data):
    """Salva os limites no arquivo JSON"""
    ensure_limits_dir()
    try:
        with open(DEFAULT_LIMITS_FILE, "w") as f:
            json.dump(limits_data, f, indent=4)
        print(f"Limites salvos em {DEFAULT_LIMITS_FILE}")
    except Exception as e:
        print(f"Erro ao salvar limites: {e}")
