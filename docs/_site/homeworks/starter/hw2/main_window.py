from PySide6.QtWidgets import QMainWindow
from board_widget import BoardWidget
from setting_window import SettingWindow
from game_logic import ReversiGame
from info_widget import InfoWidget

from ai import greedy_ai, random_ai, minimax_ai, alpha_beta_ai
from PySide6.QtWidgets import QHBoxLayout, QWidget
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reversi Game")
        self.setGeometry(100, 100, 600, 600)

        # call the setting window
        self.handle_settings()

        # status bar
        self.statusBar().showMessage("Welcome to Reversi Game")

        # menu bar
        self.menu = self.menuBar()
        self.game_menu = self.menu.addMenu("Game")
        self.new_game_action = self.game_menu.addAction("New Game")
        self.new_game_action.triggered.connect(self.handle_settings)
        self.undo_action = self.game_menu.addAction("Undo")
        self.undo_action.triggered.connect(self.handle_undo)

    def create_new_game(self):
        # create the game logic
        self.game = ReversiGame()

        # Create a central widget and set the layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Create and add the board widget to the layout
        self.board = BoardWidget(self)
        layout.addWidget(self.board)

        # Create and add the info widget to the layout
        self.info_widget = InfoWidget()
        layout.addWidget(self.info_widget)

        # calibrate the window size
        self.board_size = self.board.board_size
        self.cell_size = self.board.cell_size
        self.resize(self.board_size * self.cell_size, self.board_size * self.cell_size)

        self.board.animationFinished.connect(self.handle_animation_finished)

    def handle_settings(self):
        # create a setting window and move it to the top
        self.setting_window = SettingWindow()
        self.setting_window.settings_applied.connect(self.apply_settings)
        self.setting_window.show()

    def apply_settings(self, player1, player2):
        self.players = {"black": player1, "white": player2}
        print(self.players)
        self.human_player = []
        if player1 == "human":
            self.human_player.append("black")
        if player2 == "human":
            self.human_player.append("white")
        self.create_new_game()
        self.handle_animation_finished()

    def handle_undo(self):
        # undo the last move
        pass

    def handle_animation_finished(self):
        # update the info widget
        black_score, white_score = self.game.get_score()
        self.info_widget.update_score(black_score, white_score)
        if self.game.history_moves:
            p, r, c = self.game.history_moves[-1]
            self.info_widget.update_history(f"{p.capitalize()}: ({r}, {c})")

        if self.game.is_game_over():
            print("Game Over")
            return
        # check whether there is a valid move for the current player
        if self.game.get_valid_moves(self.game.board, self.game.current_player) == []:
            self.game.switch_player()
            self.board.update_drawing()
        if self.players[self.game.current_player] == "human":
            self.board.user_click_permit = True
        elif self.players[self.game.current_player] == "greedy":
            row, col = greedy_ai(self.game.board, self.game.current_player)
            self.board.place_piece(row, col)
        elif self.players[self.game.current_player] == "random":
            row, col = random_ai(self.game.board, self.game.current_player)
            self.board.place_piece(row, col)
        elif self.players[self.game.current_player] == "minimax" or self.players[self.game.current_player] == "alpha_beta":
            # '''
            def minimax_with_timeout(board, player, depth):
                try:
                    if self.players[player] == "minimax":
                        return minimax_ai(board, player, depth)
                    else:
                        # Implement alpha-beta pruning
                        return alpha_beta_ai(board, player, depth)
                except Exception as e:
                    print(f"Error during minimax execution: {e}")
                    return None

            best_move = None
            depth = 1
            start_time = time.time()
            time_limit = 0.5
            with ThreadPoolExecutor(max_workers=1) as executor:
                while time.time() - start_time < time_limit:
                    future = executor.submit(minimax_with_timeout, self.game.board, self.game.current_player, depth)
                    try:
                        move = future.result(timeout=time_limit - (time.time() - start_time))  # Adjust timeout to ensure total time is within 1 second
                        if move:
                            best_move = move
                        # count how many empty squares are left
                        empty_squares = sum(row.count(None) for row in self.game.board)
                        if depth >= empty_squares:
                            print("Reached maximum depth")
                            break
                        depth += 1
                    except TimeoutError:
                        # terminate the thread
                        executor._threads.clear()
                        break
            print(f"depth: {depth}")
            if best_move:
                row, col = best_move
            else:
                print("No valid move found within the time limit")
                row, col = -1, -1  # Indicate no valid move found
            self.board.place_piece(row, col)
