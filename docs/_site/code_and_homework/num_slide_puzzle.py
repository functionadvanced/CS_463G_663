from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QMessageBox
import random

class SlidingPuzzle(QMainWindow):
    def __init__(self, n):
        super().__init__()

        self.n = n  # Size of the grid (nxn)
        self.setWindowTitle(f"Sliding Puzzle ({self.n}x{self.n})")
        self.setFixedSize(100 * self.n, 100 * self.n)

        self.init_puzzle()

    def init_puzzle(self):
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QGridLayout()
        self.central_widget.setLayout(self.grid_layout)
        # Start with the solved puzzle
        self.buttons = []  # To store buttons
        self.empty_pos = (self.n - 1, self.n - 1)  # Initial empty position
        numbers = list(range(1, self.n * self.n)) + [None]
        self.grid = [numbers[i * self.n:(i + 1) * self.n] for i in range(self.n)]
        self.empty_pos = (self.n - 1, self.n - 1)

        # Randomly shuffle by sliding tiles
        for _ in range(1000):  # Perform 1000 random moves to ensure the puzzle is shuffled
        # for _ in range(4):
            self.random_slide()

        # Populate the grid layout with buttons
        for i in range(self.n):
            for j in range(self.n):
                number = self.grid[i][j]
                if number is None:
                    button = QPushButton("")
                    button.setStyleSheet("background-color: lightgray;")
                else:
                    button = QPushButton(str(number))
                    button.setStyleSheet("background-color: lightblue; font-size: 18px; color: black; font-weight: bold;")

                button.setFixedSize(75, 75)
                button.clicked.connect(lambda checked, x=i, y=j: self.move_tile(x, y))

                self.grid_layout.addWidget(button, i, j)
                self.buttons.append((button, number))

    def random_slide(self):
        x, y = self.empty_pos
        neighbors = []

        # Collect valid neighbors
        if x > 0: neighbors.append((x - 1, y))
        if x < self.n - 1: neighbors.append((x + 1, y))
        if y > 0: neighbors.append((x, y - 1))
        if y < self.n - 1: neighbors.append((x, y + 1))

        # Choose a random neighbor and swap with the empty tile
        new_x, new_y = random.choice(neighbors)
        self.grid[x][y], self.grid[new_x][new_y] = self.grid[new_x][new_y], self.grid[x][y]
        self.empty_pos = (new_x, new_y)

    def move_tile(self, x, y):
        if (x, y) == self.empty_pos:
            return

        empty_x, empty_y = self.empty_pos

        # Check if the tile is adjacent to the empty space
        if abs(x - empty_x) + abs(y - empty_y) == 1:
            # Swap the button text and update the empty position
            clicked_button = self.grid_layout.itemAtPosition(x, y).widget()
            empty_button = self.grid_layout.itemAtPosition(empty_x, empty_y).widget()

            empty_button.setText(clicked_button.text())
            empty_button.setStyleSheet("background-color: lightblue; font-size: 18px; color: black; font-weight: bold;")

            clicked_button.setText("")
            clicked_button.setStyleSheet("background-color: lightgray;")

            self.grid[empty_x][empty_y], self.grid[x][y] = self.grid[x][y], self.grid[empty_x][empty_y]
            self.empty_pos = (x, y)

            if self.check_win():
                QMessageBox.information(self, "Congratulations!", "You solved the puzzle!")
                self.init_puzzle()

    def check_win(self):
        correct_order = list(range(1, self.n * self.n)) + [None]
        current_order = [self.grid[i][j] for i in range(self.n) for j in range(self.n)]
        return current_order == correct_order

if __name__ == "__main__":
    n = 3  # Set the grid size here (e.g., 3 for 3x3, 4 for 4x4, etc.)
    app = QApplication([])
    window = SlidingPuzzle(n)
    window.show()
    app.exec()
