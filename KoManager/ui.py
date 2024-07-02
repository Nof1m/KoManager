# ui.py
import httpx
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox,
    QFileDialog, QComboBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from download import DownloadThread, obter_capitulos_por_idioma

class MangaDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gerenciador de Mangás')
        self.resize(600, 400)

        # Widgets
        self.lbl_pesquisa = QLabel('Digite o título do mangá:')
        self.txt_pesquisa = QLineEdit()
        self.btn_pesquisar = QPushButton('Pesquisar')
        self.lista_mangas = QListWidget()
        self.lbl_idioma = QLabel('Idioma dos capítulos:')
        self.cbo_idioma = QComboBox()
        self.lbl_diretorio = QLabel('Diretório de destino:')
        self.txt_diretorio = QLineEdit()
        self.btn_selecionar_diretorio = QPushButton('...')
        self.lbl_formato = QLabel('Formato das imagens:')
        self.cbo_formato = QComboBox()
        self.btn_download = QPushButton('Baixar')
        self.progresso_barra = QProgressBar()

        # Layout
        self.setup_ui()

    def setup_ui(self):
        layout_principal = QVBoxLayout()
        
        # Layout de pesquisa
        layout_pesquisa = QHBoxLayout()
        layout_pesquisa.addWidget(self.lbl_pesquisa)
        layout_pesquisa.addWidget(self.txt_pesquisa)
        layout_pesquisa.addWidget(self.btn_pesquisar)
        layout_principal.addLayout(layout_pesquisa)

        # Lista de mangás
        layout_principal.addWidget(self.lista_mangas)

        # Layout de idioma
        layout_idioma = QHBoxLayout()
        layout_idioma.addWidget(self.lbl_idioma)
        layout_idioma.addWidget(self.cbo_idioma)
        layout_principal.addLayout(layout_idioma)

        # Layout de diretório
        layout_diretorio = QHBoxLayout()
        layout_diretorio.addWidget(self.lbl_diretorio)
        layout_diretorio.addWidget(self.txt_diretorio)
        layout_diretorio.addWidget(self.btn_selecionar_diretorio)
        layout_principal.addLayout(layout_diretorio)

        # Layout de formato
        layout_formato = QHBoxLayout()
        layout_formato.addWidget(self.lbl_formato)
        layout_formato.addWidget(self.cbo_formato)
        layout_principal.addLayout(layout_formato)

        # Botão de download e barra de progresso
        layout_principal.addWidget(self.btn_download)
        layout_principal.addWidget(self.progresso_barra)

        # Set Layout
        self.setLayout(layout_principal)

        
        self.btn_pesquisar.clicked.connect(self.pesquisar_manga)
        self.btn_selecionar_diretorio.clicked.connect(self.selecionar_diretorio)
        self.btn_download.clicked.connect(self.iniciar_download)

        
        self.cbo_idioma.addItems(['en', 'pt-br'])
        self.cbo_formato.addItems(['jpg', 'cbz'])

    def pesquisar_manga(self):
        pesquisa = self.txt_pesquisa.text()
        base_url = "https://api.mangadex.org/"

        r = httpx.get(
            f"{base_url}/manga",
            params={"title": pesquisa}
        )

        if r.status_code == 200:
            self.lista_mangas.clear()
            self.mangas = r.json()["data"]  

            if self.mangas:
                for manga in self.mangas:
                    self.lista_mangas.addItem(manga['attributes']['title']['en'])
            else:
                QMessageBox.information(self, 'Informação', 'Nenhum mangá encontrado.')

        else:
            QMessageBox.warning(self, 'Erro', f"Erro ao fazer requisição: {r.status_code}")
        pass

    def selecionar_diretorio(self):
        diretorio = QFileDialog.getExistingDirectory(self, 'Selecionar diretório')
        if diretorio:
            self.txt_diretorio.setText(diretorio)
        pass

    def iniciar_download(self):
        item_selecionado = self.lista_mangas.currentItem()
        if not item_selecionado:
            QMessageBox.warning(self, 'Aviso', 'Selecione um mangá.')
            return

        escolha = self.lista_mangas.currentRow()

        if hasattr(self, 'mangas'):
            manga_id = self.mangas[escolha]['id']
        else:
            QMessageBox.warning(self, 'Aviso', 'Realize a pesquisa antes de baixar o mangá.')
            return

        idioma = self.cbo_idioma.currentText()

        capitulos = obter_capitulos_por_idioma(manga_id, idioma)

        if not capitulos:
            QMessageBox.warning(self, 'Aviso', 'Nenhum capítulo encontrado.')
            return

        diretorio = self.txt_diretorio.text()
        formato_imagem = self.cbo_formato.currentText()

        
        self.download_thread = DownloadThread(capitulos, diretorio, formato_imagem)
        self.download_thread.progress_changed.connect(self.atualizar_progresso)
        self.download_thread.finished.connect(self.download_concluido)
        self.download_thread.start()
        pass

    def atualizar_progresso(self, valor):
        self.progresso_barra.setValue(valor)


    def download_concluido(self): 
        QMessageBox.information(self, 'Informação', 'Download concluído!')