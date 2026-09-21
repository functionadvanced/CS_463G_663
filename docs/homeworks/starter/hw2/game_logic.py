class ReversiGame:
    def __init__(self):
        self.board_size = 8
        self.board = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]
        self.current_player = "black" # black always starts first
        self.history_boards = []
        self.history_moves = []
        self.initialize_board()

    def initialize_board(self):
        mid = self.board_size // 2
        self.board[mid - 1][mid - 1] = "white"
        self.board[mid][mid] = "white"
        self.board[mid - 1][mid] = "black"
        self.board[mid][mid - 1] = "black"

    def switch_player(self):
        self.current_player = "white" if self.current_player == "black" else "black"

    def is_valid_move(self, row, col, board, player):
        if board[row][col] is not None:
            return False

        opponent = "black" if player == "white" else "white"
        directions = [
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),
            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1),
        ]

        for d_row, d_col in directions:
            r, c = row + d_row, col + d_col
            if (
                not (0 <= r < self.board_size and 0 <= c < self.board_size)
                or board[r][c] != opponent
            ):
                continue

            r += d_row
            c += d_col
            while 0 <= r < self.board_size and 0 <= c < self.board_size:
                if board[r][c] is None:
                    break
                if board[r][c] == player:
                    return True
                r += d_row
                c += d_col

        return False

    def get_valid_moves(self, board, player):
        valid_moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.is_valid_move(row, col, board, player):
                    valid_moves.append((row, col))
        return valid_moves

    def change_pieces(self, row, col, board, player):
        changed_pieces = []
        opponent = "black" if player == "white" else "white"
        directions = [
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),
            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1),
        ]
        for d_row, d_col in directions:
            r, c = row + d_row, col + d_col
            if (
                not (0 <= r < self.board_size and 0 <= c < self.board_size)
                or board[r][c] != opponent
            ):
                continue

            r += d_row
            c += d_col
            while 0 <= r < self.board_size and 0 <= c < self.board_size:
                if board[r][c] is None:
                    break
                if board[r][c] == player:
                    r, c = row + d_row, col + d_col
                    while board[r][c] == opponent:
                        changed_pieces.append((r, c))
                        board[r][c] = player
                        r += d_row
                        c += d_col
                    break
                r += d_row
                c += d_col
        return changed_pieces

    def is_game_over(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.is_valid_move(
                    row, col, self.board, "black"
                ) or self.is_valid_move(row, col, self.board, "white"):
                    return False
        return True

    def get_score(self):
        black_score = sum(row.count("black") for row in self.board)
        white_score = sum(row.count("white") for row in self.board)
        return black_score, white_score

    def place_piece(self, row, col):
        changed_pieces = []
        if self.is_valid_move(row, col, self.board, self.current_player):
            self.history_boards.append([row[:] for row in self.board]) # deep copy the board to save the state
            self.history_moves.append((self.current_player, row, col))
            self.board[row][col] = self.current_player
            changed_pieces = self.change_pieces(
                row, col, self.board, self.current_player
            )
            self.switch_player()
        return changed_pieces
