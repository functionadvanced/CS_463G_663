from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget

class InfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.history_moves = []
        self.current_score = {'Black': 0, 'White': 0}

        self.layout = QVBoxLayout(self)

        self.history_label = QLabel("History Moves")
        self.layout.addWidget(self.history_label)

        self.history_listbox = QListWidget()
        self.layout.addWidget(self.history_listbox)

        self.score_label = QLabel("Current Score")
        self.layout.addWidget(self.score_label)

        self.score_text = QLabel(f"Black: {self.current_score['Black']}  White: {self.current_score['White']}")
        self.layout.addWidget(self.score_text)

    def update_history(self, move):
        self.history_moves.append(move)
        self.history_listbox.addItem(move)

    def update_score(self, black_score, white_score):
        self.current_score['Black'] = black_score
        self.current_score['White'] = white_score
        self.score_text.setText(f"Black: {self.current_score['Black']}  White: {self.current_score['White']}")

if __name__ == "__main__":
    app = QApplication([])

    info_widget = InfoWidget()
    info_widget.setWindowTitle("Info Widget")
    info_widget.show()

    app.exec()