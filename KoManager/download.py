# download.py

import os
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor, wait, TimeoutError
import httpx
from PyQt6.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    progress_changed = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, capitulos, diretorio, formato_imagem):
        super().__init__()
        self.capitulos = capitulos
        self.diretorio = diretorio
        self.formato_imagem = formato_imagem

    def run(self):
        total_capitulos = len(self.capitulos)
        self.progress_changed.emit(0)

        for index, capitulo in enumerate(self.capitulos, 1):
            salvar_capitulo(capitulo, self.diretorio, self.formato_imagem)
            progresso = int(index / total_capitulos * 100)
            self.progress_changed.emit(progresso)

        self.finished.emit()

def obter_capitulos_por_idioma(manga_id, idioma):
    url = "https://api.mangadex.org/"
    endpoint = f"manga/{manga_id}/feed"

    params = {
        "translatedLanguage[]": idioma,
        "order[chapter]": "asc",
        "limit": 500
    }
    r = httpx.Client().get(f"{url}{endpoint}", params=params)

    if r.status_code == 200:
        capitulos = r.json()["data"]
        return capitulos
    else:
        print(f"Erro ao obter capítulos: {r.status_code}")
        return None

def download_page(session, base_url, hash_, page, capitulo_dir):
    url = f"{base_url}/data/{hash_}/{page}"
    response = session.get(url)
    if response.status_code == 200:
        file_name = os.path.basename(page)
        with open(os.path.join(capitulo_dir, file_name), mode="wb") as f:
            f.write(response.content)
    else:
        print(f"Erro ao baixar página {page}, status {response.status_code}")

def salvar_capitulo(capitulo, diretorio, formato_imagem):
    imagens_id = capitulo['id']
    imagens_url = httpx.get(f"https://api.mangadex.org/at-home/server/{imagens_id}").json()
    capitulo_number = capitulo['attributes']['chapter']

    capitulo_dir = os.path.join(diretorio, f"Capítulo {capitulo_number}")
    os.makedirs(capitulo_dir, exist_ok=True)

    print(f"Baixando capítulo {capitulo_number}")

    base_url = imagens_url['baseUrl']
    hash_ = imagens_url['chapter']['hash']
    pages = imagens_url['chapter']['data']

    with ThreadPoolExecutor(max_workers=10) as executor:
        session = httpx.Client()
        futures = []
        for page in pages:
            futures.append(executor.submit(download_page, session, base_url, hash_, page, capitulo_dir))

        try:
            wait(futures)
        except TimeoutError as e:
            print(f"Timeout error occurred: {e}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            
        finally:
            session.close()

    if formato_imagem == "cbz":
        temp_files = [os.path.join(capitulo_dir, page) for page in os.listdir(capitulo_dir)]
        criar_cbz(temp_files, capitulo_dir)
        for temp_file in temp_files:
            os.remove(temp_file)
        shutil.rmtree(capitulo_dir)

def criar_cbz(temp_files, capitulo_dir):
    with zipfile.ZipFile(f"{capitulo_dir}.cbz", 'w') as cbz_file:
        for temp_file in temp_files:
            filename = os.path.basename(temp_file)
            cbz_file.write(temp_file, arcname=filename)

    print(f"CBZ criado: {capitulo_dir}.cbz")
