import os
from ftplib import FTP
from datetime import datetime

FTP_HOST = "3.138.161.165"
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

paths = {
    "fazenda": "Bom_Retiro",
    "coca_cola": "Porto_Real"
}

LOCAL_DIR = "data/downloads"

def download_latest_file(station_key):
    try:
        remote_dir = paths.get(station_key)
        if not remote_dir:
            print(f"[ERRO] Estação '{station_key}' não está mapeada no dicionário de paths.")
            return None, None

        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(remote_dir)

        files = [f for f in ftp.nlst() if f.endswith(".lsi")]

        if not files:
            print(f"[{station_key.upper()}] Nenhum arquivo .lsi encontrado no diretório '{remote_dir}'")
            return None, None

        files.sort(key=lambda name: get_datetime_from_filename(name), reverse=True)
        latest_file = files[0]

        local_path = os.path.join(LOCAL_DIR, station_key)
        os.makedirs(local_path, exist_ok=True)
        local_file_path = os.path.join(local_path, latest_file)

        with open(local_file_path, "wb") as f:
            ftp.retrbinary(f"RETR " + latest_file, f.write)

        ftp.quit()

        print(f"[{station_key.upper()}] ✔ Arquivo baixado: {latest_file}")
        print(f"[{station_key.upper()}] ✔ Caminho local salvo: {local_file_path}")

        return local_file_path, latest_file

    except Exception as e:
        print(f"[ERRO] Durante download da estação '{station_key}': {e}")
        return None, None

def get_datetime_from_filename(filename):
    try:
        base = filename.split("..")[0]
        return datetime.strptime(base, "%d_%m_%Y %H_%M")
    except Exception:
        return datetime.min
