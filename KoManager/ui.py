# ui.py
import httpx
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
     QMessageBox, QFileDialog, QMainWindow
)
from download import DownloadThread, obter_capitulos_por_idioma
from uiko import Ui_MainWindow  


class MangaDownloader(QMainWindow):
    def __init__(self):
        super().__init__()

        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        
        self.setWindowTitle('KoManager')
        self.resize(800, 600)
        self.setWindowIcon(QIcon('KoManagerico.ico'))
        self.setMinimumSize(QSize(170, 0))
        self.setMaximumSize(QSize(1280, 720))

        
        self.ui.pushButton.clicked.connect(self.pesquisar_manga)
        self.ui.pushButton_2.clicked.connect(self.selecionar_diretorio)
        self.ui.pushButton_3.clicked.connect(self.iniciar_download)

        
        self.ui.comboBox.addItems(['en', 'pt-br'])
        self.ui.comboBox_2.addItems(['jpg', 'cbz'])

    def pesquisar_manga(self):
        pesquisa = self.ui.lineEdit.text()
        base_url = "https://api.mangadex.org/"

        r = httpx.get(
            f"{base_url}/manga",
            params={"title": pesquisa}
        )

        if r.status_code == 200:
            self.ui.listWidget.clear()
            self.mangas = r.json()["data"]

            if self.mangas:
                for manga in self.mangas:
                    self.ui.listWidget.addItem(manga['attributes']['title']['en'])
            else:
                QMessageBox.information(self, 'Informação', 'Nenhum mangá encontrado.')

        else:
            QMessageBox.warning(self, 'Erro', f"Erro ao fazer requisição: {r.status_code}")

    def selecionar_diretorio(self):
        diretorio = QFileDialog.getExistingDirectory(self, 'Selecionar diretório')
        if diretorio:
            self.ui.lineEdit_2.setText(diretorio)

    def iniciar_download(self):
        item_selecionado = self.ui.listWidget.currentItem()
        if not item_selecionado:
            QMessageBox.warning(self, 'Aviso', 'Selecione um mangá.')
            return

        escolha = self.ui.listWidget.currentRow()

        if hasattr(self, 'mangas'):
            manga_id = self.mangas[escolha]['id']
        else:
            QMessageBox.warning(self, 'Aviso', 'Realize a pesquisa antes de baixar o mangá.')
            return

        idioma = self.ui.comboBox.currentText()

        capitulos = obter_capitulos_por_idioma(manga_id, idioma)

        if not capitulos:
            QMessageBox.warning(self, 'Aviso', 'Nenhum capítulo encontrado.')
            return

        diretorio = self.ui.lineEdit_2.text()
        formato_imagem = self.ui.comboBox_2.currentText()

        self.download_thread = DownloadThread(capitulos, diretorio, formato_imagem)
        self.download_thread.progress_changed.connect(self.atualizar_progresso)
        self.download_thread.finished.connect(self.download_concluido)
        self.download_thread.start()

    def atualizar_progresso(self, valor):
        self.ui.progressBar.setValue(valor)

    def download_concluido(self):
        QMessageBox.information(self, 'Informação', 'Download concluído!')


