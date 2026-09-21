from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QMouseEvent
from PySide6.QtCore import QThread
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal


class BoardWidget(QWidget):
    animationFinished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board_size = parent.game.board_size
        self.cell_size = 70  # Cell size in pixels
        self.padding_size = self.cell_size // 7  # Padding size of each cell in pixels
        self.hint_size = 10
        self.setMinimumSize(
            self.board_size * self.cell_size, self.board_size * self.cell_size
        )
        self.game = parent.game
        self.human_player = parent.human_player
        self.parent = parent
        self.changed_pieces = []
        self.animation_frames = 20
        self.animation_step = 0
        self.old_board = [row[:] for row in self.game.board]
        self.current_move = None
        self.user_click_permit = False  # Permit user to click on the board

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        cell_color = [QColor("green"), QColor("darkgreen")]

        # Draw the old board
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = cell_color[(row + col) % 2]
                painter.fillRect(
                    col * self.cell_size,
                    row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                    color,
                )

                if (row, col) in self.changed_pieces:
                    continue

                if self.old_board[row][col] == "black":
                    color = QColor("black")
                elif self.old_board[row][col] == "white":
                    color = QColor("white")
                if self.old_board[row][col] is not None:
                    painter.setBrush(color)
                    painter.drawEllipse(
                        col * self.cell_size + self.padding_size,
                        row * self.cell_size + self.padding_size,
                        self.cell_size - 2 * self.padding_size,
                        self.cell_size - 2 * self.padding_size,
                    )



        # Highlight all possible moves
        possible_moves = self.game.get_valid_moves(
            self.game.board, self.game.current_player
        )
        for move in possible_moves:
            row, col = move
            painter.setBrush(QColor("red"))
            painter.drawEllipse(
                col * self.cell_size + self.cell_size // 2 - self.hint_size // 2,
                row * self.cell_size + self.cell_size // 2 - self.hint_size // 2,
                self.hint_size,
                self.hint_size,
            )

        if self.current_move:
            row, col = self.current_move
            painter.setBrush(QColor(self.game.board[row][col]))
            painter.drawEllipse(
                col * self.cell_size + self.padding_size,
                row * self.cell_size + self.padding_size,
                self.cell_size - 2 * self.padding_size,
                self.cell_size - 2 * self.padding_size,
            )
            # highlight the current move
            painter.setBrush(QColor("blue"))
            painter.drawEllipse(
                col * self.cell_size + self.cell_size // 2 - self.hint_size // 2,
                row * self.cell_size + self.cell_size // 2 - self.hint_size // 2,
                self.hint_size,
                self.hint_size,
            )
        painter.end()
        # Start the animation for changed pieces
        if self.changed_pieces:

            duration = 500  # Duration in milliseconds
            interval = duration // self.animation_frames
            step = self.animation_step
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            alpha = min(255, int(255 * (step + 1) / self.animation_frames))
            for row, col in self.changed_pieces:
                new_color = self.game.board[row][col]
                color = QColor("black") if new_color == "black" else QColor("white")
                color.setAlpha(alpha)
                painter.setBrush(color)
                painter.drawEllipse(
                    col * self.cell_size + self.padding_size,
                    row * self.cell_size + self.padding_size,
                    self.cell_size - 2 * self.padding_size,
                    self.cell_size - 2 * self.padding_size,
                )
            painter.end()

            if not self.animation_step >= self.animation_frames:
                self.animation_step += 1
                self.update()
                QThread.msleep(interval)
            else:
                # Update old board after animation ends
                self.old_board = [row[:] for row in self.game.board]
                self.animation_step = 0
                self.changed_pieces = []
                self.animationFinished.emit()  # emit a signal showing the animation is finished

    def update_drawing(self):
        self.update()
        # emit a signal to the main window to update the status bar
        black_score, white_score = self.game.get_score()
        self.parent.statusBar().showMessage(
            f"{self.game.current_player.capitalize()}'s Turn - Black: {black_score}, White: {white_score}"
        )

    def place_piece(self, row, col):
        self.changed_pieces = self.game.place_piece(row, col)
        self.current_move = (row, col)
        self.update_drawing()

    def mousePressEvent(self, event: QMouseEvent):
        # if not the player's turn, do nothing
        if self.game.current_player not in self.human_player or not self.user_click_permit:
            return
        col = event.x() // self.cell_size
        row = event.y() // self.cell_size
        if not self.game.is_valid_move(
            row, col, self.game.board, self.game.current_player
        ):
            return
        self.user_click_permit = False
        self.place_piece(row, col)

