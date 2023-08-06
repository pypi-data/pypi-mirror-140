# Copyright 2022 iiPython

# Modules
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QApplication

# Main window
class MainWindow(QMainWindow):
    def __init__(self, url: str, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)
        self.browser.loadFinished.connect(self.update_title)
        self.setCentralWidget(self.browser)
        self.show()

    def update_title(self) -> None:
        self.setWindowTitle(self.browser.page().title())

# Launcher
def load_page(url: str) -> None:
    app = QApplication([])
    app.setApplicationName("Nitrogen")
    w = MainWindow(url)  # noqa
    app.exec_()
