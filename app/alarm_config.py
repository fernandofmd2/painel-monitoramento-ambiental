import json
import os

# Pasta onde salvaremos os limites separados por estação
LIMITS_DIR = "limits"

# Cria a pasta se não existir
os.makedirs(LIMITS_DIR, exist_ok=True)

# Lista padrão de parâmetros
DEFAULT_PARAMS = [
    "O3", "CO", "SO2", "NO", "NO2", "NOX", "PM10",
    "Temperatura", "Umidade Relativa", "Pressão Atmosférica",
    "Direção do vento", "Velocidade do vento", "Índice Pluviométrico"
]

# Valores default para cada parâmetro
DEFAULT_LIMITS = {param: {"min": 0.0, "max": 9999.0} for param in DEFAULT_PARAMS}

def get_limits_path(station_key: str) -> str:
    """Retorna o caminho do arquivo JSON da estação"""
    return os.path.join(LIMITS_DIR, f"limits_{station_key}.json")

def load_limits(station_key: str = None):
    """
    Carrega limites.
    - Se `station_key` for informado, carrega apenas dessa estação.
    - Se não for, carrega todas as estações que existirem.
    """
    # Se queremos apenas uma estação específica
    if station_key:
        path = get_limits_path(station_key)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        else:
            return DEFAULT_LIMITS.copy()

    # Se queremos tudo, carrega todos os arquivos existentes
    all_limits = {}
    for file in os.listdir(LIMITS_DIR):
        if file.startswith("limits_") and file.endswith(".json"):
            st_key = file.replace("limits_", "").replace(".json", "")
            with open(os.path.join(LIMITS_DIR, file), "r") as f:
                all_limits[st_key] = json.load(f)

    # Se não encontrou nada, cria as duas estações padrão
    if not all_limits:
        all_limits = {
            "fazenda": DEFAULT_LIMITS.copy(),
            "coca_cola": DEFAULT_LIMITS.copy()
        }
    return all_limits

def save_limits(station_key: str, limits_data: dict):
    """Salva os limites da estação específica em JSON"""
    path = get_limits_path(station_key)
    with open(path, "w") as f:
        json.dump(limits_data, f, indent=4)
