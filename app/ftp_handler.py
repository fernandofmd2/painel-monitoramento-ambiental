from ftplib import FTP
import os

FTP_HOST = "3.138.161.165"
FTP_USER = "guardian-rj"
FTP_PASS = "guardian.aires2025"

# Mapeamento das estações e diretórios remotos
STATIONS = {
    "fazenda": "Bom_Retiro",
    "coca_cola": "Porto_Real"
}

# Pasta local onde os arquivos baixados serão salvos
DOWNLOAD_DIR = "data/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_latest_file(ftp, directory):
    """Obtém o último arquivo mais recente pela data de modificação do FTP"""
    ftp.cwd(directory)
    file_list = ftp.nlst()

    if not file_list:
        return None

    # Pega a data/hora de modificação (MDTM)
    files_with_dates = []
    for filename in file_list:
        try:
            modified_time = ftp.sendcmd(f"MDTM {filename}")[4:].strip()  # formato YYYYMMDDHHMMSS
            files_with_dates.append((filename, modified_time))
        except:
            pass  # Ignora se não conseguir pegar a data

    if not files_with_dates:
        return sorted(file_list)[-1]  # fallback: pega o último por ordem alfabética

    # Ordena pela data mais recente
    latest_file = sorted(files_with_dates, key=lambda x: x[1], reverse=True)[0][0]
    return latest_file

def download_latest_file(station_key):
    """Baixa o último arquivo mais recente para a estação especificada"""
    if station_key not in STATIONS:
        return None, None

    remote_dir = STATIONS[station_key]
    local_station_dir = os.path.join(DOWNLOAD_DIR, station_key)
    os.makedirs(local_station_dir, exist_ok=True)

    with FTP(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)

        # Obtém o último arquivo modificado
        latest_filename = get_latest_file(ftp, remote_dir)
        if not latest_filename:
            return None, None

        local_path = os.path.join(local_station_dir, latest_filename)

        # Baixa o arquivo
        with open(local_path, "wb") as f:
            ftp.retrbinary(f"RETR {remote_dir}/{latest_filename}", f.write)

        return local_path, latest_filename
