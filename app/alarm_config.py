import json
import os

# Diretório para salvar limites
LIMITS_DIR = "limits"
os.makedirs(LIMITS_DIR, exist_ok=True)

# Arquivos por estação
FILES = {
    "Fazenda": os.path.join(LIMITS_DIR, "fazenda_limits.json"),
    "Coca Cola": os.path.join(LIMITS_DIR, "coca_cola_limits.json"),
}

# Limites padrão
DEFAULT_LIMITS = {
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

def load_limits():
    """Carrega os limites de todas as estações"""
    limits = {}
    for station, filepath in FILES.items():
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                limits[station] = json.load(f)
        else:
            limits[station] = DEFAULT_LIMITS.copy()
    return limits

def save_limits(limits):
    """Salva os limites de cada estação em arquivos separados"""
    for station, filepath in FILES.items():
        if station in limits:
            with open(filepath, "w") as f:
                json.dump(limits[station], f, indent=4)
