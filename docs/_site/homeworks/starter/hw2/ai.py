import random
def is_valid_move(row, col, board, player):
    if board[row][col] is not None:
        return False

    opponent = "black" if player == "white" else "white"
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    for d_row, d_col in directions:
        r, c = row + d_row, col + d_col
        if not (0 <= r < len(board) and 0 <= c < len(board)) or board[r][c] != opponent:
            continue

        r += d_row
        c += d_col
        while 0 <= r < len(board) and 0 <= c < len(board):
            if board[r][c] is None:
                break
            if board[r][c] == player:
                return True
            r += d_row
            c += d_col

    return False


def change_pieces(row, col, board, player):
    opponent = "black" if player == "white" else "white"
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    for d_row, d_col in directions:
        r, c = row + d_row, col + d_col
        if not (0 <= r < len(board) and 0 <= c < len(board)) or board[r][c] != opponent:
            continue

        r += d_row
        c += d_col
        while 0 <= r < len(board) and 0 <= c < len(board):
            if board[r][c] is None:
                break
            if board[r][c] == player:
                r, c = row + d_row, col + d_col
                while board[r][c] == opponent:
                    board[r][c] = player
                    r += d_row
                    c += d_col
                break
            r += d_row
            c += d_col




def random_ai(board, player):
    valid_moves = []
    for row in range(len(board)):
        for col in range(len(board)):
            if is_valid_move(row, col, board, player):
                valid_moves.append((row, col))

    if not valid_moves:
        return None

    return random.choice(valid_moves)

def utility(board, player):
    # Your code here
    pass

def greedy_ai(board, player):
    # Your code here
    pass

def minimax_ai(board, player, depth):
    # Your code here
    pass

def alpha_beta_ai(board, player, depth):
    # Your code here
    pass