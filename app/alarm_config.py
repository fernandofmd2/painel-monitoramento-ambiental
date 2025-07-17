import json
import os

CONFIG_FILE = "data/config.json"

# Todos os 13 parâmetros com limites iniciais padrão
DEFAULT_LIMITS = {
    "O3": {"min": 0.0, "max": 200.0},
    "CO": {"min": 0.0, "max": 10.0},
    "SO2": {"min": 0.0, "max": 5.0},
    "NO": {"min": 0.0, "max": 5.0},
    "NO2": {"min": 0.0, "max": 5.0},
    "NOX": {"min": 0.0, "max": 10.0},
    "PM10": {"min": 0.0, "max": 150.0},
    "Temperatura": {"min": -10.0, "max": 50.0},
    "Umidade Relativa": {"min": 0.0, "max": 100.0},
    "Pressão Atmosférica": {"min": 900.0, "max": 1100.0},
    "Velocidade do vento": {"min": 0.0, "max": 30.0},
    "Direção do vento": {"min": 0.0, "max": 360.0},
    "Índice Pluviométrico": {"min": 0.0, "max": 100.0}
}

def load_limits():
    if not os.path.exists(CONFIG_FILE):
        save_limits(DEFAULT_LIMITS)
        return DEFAULT_LIMITS
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    # Garante que todos os parâmetros estejam sempre presentes
    for param in DEFAULT_LIMITS:
        if param not in data:
            data[param] = DEFAULT_LIMITS[param]
    return data

def save_limits(limits):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(limits, f, indent=2)
