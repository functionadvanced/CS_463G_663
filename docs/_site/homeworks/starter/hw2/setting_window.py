from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt


class SettingWindow(QMainWindow):
    settings_applied = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 300, 300)
        # always put the window on top
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.initUI()
        # resize the window to fit the content
        # set minimum width to prevent resizing
        self.setMinimumWidth(300)
        self.adjustSize()

    def initUI(self):
        layout = QVBoxLayout()

        self.player1_label = QLabel("Player 1 (Black):")
        layout.addWidget(self.player1_label)

        all_players = ['human', 'greedy', 'random', 'minimax', 'alpha_beta']

        self.player1_combo = QComboBox()
        self.player1_combo.addItems(all_players)
        layout.addWidget(self.player1_combo)

        self.player2_label = QLabel("Player 2 (White):")
        layout.addWidget(self.player2_label)

        self.player2_combo = QComboBox()
        self.player2_combo.addItems(all_players)
        layout.addWidget(self.player2_combo)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def save_settings(self):
        player1 = self.player1_combo.currentText()
        player2 = self.player2_combo.currentText()

        # emit a signal to the main window to apply the settings
        self.settings_applied.emit(player1, player2)
        self.close()


if __name__ == "__main__":  # test the SettingWindow class
    app = QApplication([])
    window = SettingWindow()
    window.show()
    app.exec()
