def parse_lsi_file(filepath, station):
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    print(f"\n📂 [{station.upper()}] Conteúdo bruto:")
    print(raw[:300])

    # Detecta marcador
    if "AM," in raw:
        values_str = raw.split("AM,", 1)[1]
    elif "PM," in raw:
        values_str = raw.split("PM,", 1)[1]
    else:
        print(f"[{station.upper()}] ❌ Nenhum 'AM,' ou 'PM,' encontrado.")
        return {}

    # Divide todos os valores após "AM," ou "PM,"
    tokens = [v.strip() for v in values_str.split(",") if v.strip()]
    
    # Pega apenas os valores que estão nas posições pares (0, 2, 4...) — ignorando os "1"
    values = tokens[::2]

    print(f"[{station.upper()}] ✅ Valores extraídos: {values}")

    if len(values) < 13:
        print(f"[{station.upper()}] ❌ Menos de 13 valores após limpeza.")
        return {}

    if station == "coca_cola":
        keys = [
            "SO2", "O3", "CO",
            "Velocidade do vento", "Direção do vento",
            "Índice Pluviométrico", "Pressão Atmosférica",
            "PM10", "Temperatura", "Umidade Relativa",
            "NO", "NO2", "NOX"
        ]
    else:
        keys = [
            "NO", "NO2", "NOX",
            "CO", "SO2", "O3",
            "Temperatura", "Umidade Relativa", "Pressão Atmosférica",
            "PM10", "Direção do vento", "Velocidade do vento", "Índice Pluviométrico"
        ]

    parsed = {}
    for k, v in zip(keys, values):
        try:
            parsed[k] = float(v)
        except ValueError:
            parsed[k] = None

    print(f"[{station.upper()}] ✅ Dados finais:", parsed)
    return parsed
