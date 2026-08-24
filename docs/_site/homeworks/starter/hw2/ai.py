import random

DIRECTIONS = (
    (0, 1),
    (1, 0),
    (0, -1),
    (-1, 0),
    (1, 1),
    (-1, -1),
    (1, -1),
    (-1, 1),
)


def opponent_of(player):
    return "white" if player == "black" else "black"


def is_valid_move(row, col, board, player):
    size = len(board)
    if not (0 <= row < size and 0 <= col < size):
        return False
    if board[row][col] is not None:
        return False

    opponent = opponent_of(player)
    for d_row, d_col in DIRECTIONS:
        r, c = row + d_row, col + d_col
        if not (0 <= r < size and 0 <= c < size):
            continue
        if board[r][c] != opponent:
            continue

        r += d_row
        c += d_col
        while 0 <= r < size and 0 <= c < size:
            if board[r][c] is None:
                break
            if board[r][c] == player:
                return True
            r += d_row
            c += d_col
    return False


def change_pieces(row, col, board, player):
    """Flip captured discs in a board that already contains the new disc."""
    opponent = opponent_of(player)
    size = len(board)
    for d_row, d_col in DIRECTIONS:
        r, c = row + d_row, col + d_col
        captured = []
        while (
            0 <= r < size
            and 0 <= c < size
            and board[r][c] == opponent
        ):
            captured.append((r, c))
            r += d_row
            c += d_col

        if (
            captured
            and 0 <= r < size
            and 0 <= c < size
            and board[r][c] == player
        ):
            for captured_row, captured_col in captured:
                board[captured_row][captured_col] = player


def legal_moves(board, player):
    return [
        (row, col)
        for row in range(len(board))
        for col in range(len(board[row]))
        if is_valid_move(row, col, board, player)
    ]


def board_after_move(board, player, move):
    row, col = move
    if not is_valid_move(row, col, board, player):
        raise ValueError(f"illegal move for {player}: {move}")
    next_board = [values[:] for values in board]
    next_board[row][col] = player
    change_pieces(row, col, next_board, player)
    return next_board


def is_terminal(board):
    return not legal_moves(board, "black") and not legal_moves(
        board, "white"
    )


def random_ai(board, player):
    moves = legal_moves(board, player)
    return random.choice(moves) if moves else None


def utility(board, player):
    """Evaluate board from player's perspective."""
    raise NotImplementedError("Implement utility")


def greedy_ai(board, player):
    """Return a legal immediate-gain move, or None for a forced pass."""
    raise NotImplementedError("Implement greedy_ai")


def minimax_ai(board, player, depth):
    """Return a legal depth-limited minimax move."""
    raise NotImplementedError("Implement minimax_ai")


def alpha_beta_ai(board, player, depth):
    """Return a legal minimax move using alpha-beta pruning."""
    raise NotImplementedError("Implement alpha_beta_ai")
