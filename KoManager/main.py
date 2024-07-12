# main.py

import sys
from PyQt6.QtWidgets import QApplication
from ui import MangaDownloader

def main():
    app = QApplication(sys.argv)
    mainWindow = MangaDownloader()
    mainWindow.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
