from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton,
    QMessageBox,
)
import sys


class TicTacToe(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"  # Human player is 'X'

    def initUI(self):
        self.setWindowTitle("Tic-Tac-Toe")
        self.setGeometry(100, 100, 300, 300)
        self.layout = QGridLayout()
        self.buttons = [[QPushButton("") for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                self.buttons[i][j].setFixedSize(100, 100)
                self.buttons[i][j].clicked.connect(
                    lambda _, x=i, y=j: self.make_move(x, y)
                )
                self.layout.addWidget(self.buttons[i][j], i, j)
        # make all buttons' text size bigger
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].setStyleSheet("font-size: 40px; font-weight: bold")
        self.setLayout(self.layout)

    def make_move(self, x, y):
        if self.board[x][y] == "" and self.current_player == "X":
            self.board[x][y] = "X"
            self.buttons[x][y].setText("X")
            if self.check_winner("X"):
                self.game_over("X wins!")
                return
            self.current_player = "O"
            self.ai_move()

    def ai_move(self):
        best_score = -float("inf")
        best_move = None

        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    self.board[i][j] = "O"
                    score = self.minimax(False)
                    self.board[i][j] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)

        if best_move:
            x, y = best_move
            self.board[x][y] = "O"
            self.buttons[x][y].setText("O")
            if self.check_winner("O"):
                self.game_over("O wins!")
                return
            self.current_player = "X"
        elif self.is_draw():
            self.game_over("It's a draw!")

    def minimax(self, is_maximizing):
        if self.check_winner("O"):
            return 1
        if self.check_winner("X"):
            return -1
        if self.is_draw():
            return 0

        if is_maximizing:
            best_score = -float("inf")
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "":
                        self.board[i][j] = "O"
                        score = self.minimax(False)
                        self.board[i][j] = ""
                        best_score = max(best_score, score)
            return best_score
        else:
            best_score = float("inf")
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "":
                        self.board[i][j] = "X"
                        score = self.minimax(True)
                        self.board[i][j] = ""
                        best_score = min(best_score, score)
            return best_score

    def check_winner(self, player):
        for row in self.board:
            if all(cell == player for cell in row):
                return True
        for col in range(3):
            if all(self.board[row][col] == player for row in range(3)):
                return True
        if all(self.board[i][i] == player for i in range(3)) or all(
            self.board[i][2 - i] == player for i in range(3)
        ):
            return True
        return False

    def is_draw(self):
        return all(self.board[i][j] != "" for i in range(3) for j in range(3))

    def game_over(self, message):
        QMessageBox.information(self, "Game Over", message)
        self.reset_board()

    def reset_board(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].setText("")
        self.current_player = "X"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = TicTacToe()
    game.show()
    sys.exit(app.exec())
