from ai import board_after_move, legal_moves, opponent_of, random_ai

BLACK = "black"
WHITE = "white"


def initial_board():
    board = [[None for _ in range(8)] for _ in range(8)]
    board[3][3] = WHITE
    board[4][4] = WHITE
    board[3][4] = BLACK
    board[4][3] = BLACK
    return board


def score(board):
    return {
        BLACK: sum(row.count(BLACK) for row in board),
        WHITE: sum(row.count(WHITE) for row in board),
    }


def render_board(board):
    symbols = {None: ".", BLACK: "B", WHITE: "W"}
    lines = ["  0 1 2 3 4 5 6 7"]
    for row, values in enumerate(board):
        lines.append(f"{row} " + " ".join(symbols[value] for value in values))
    counts = score(board)
    lines.append(f"Black: {counts[BLACK]}  White: {counts[WHITE]}")
    return "\n".join(lines)


def run_game(black_agent, white_agent, verbose=False):
    """Run one complete game and return its board, scores, and winner."""
    agents = {BLACK: black_agent, WHITE: white_agent}
    board = initial_board()
    player = BLACK
    consecutive_passes = 0

    while consecutive_passes < 2:
        moves = legal_moves(board, player)
        if not moves:
            consecutive_passes += 1
            if verbose:
                print(f"{player} passes")
            player = opponent_of(player)
            continue

        consecutive_passes = 0
        board_before = [row[:] for row in board]
        move = agents[player](board_before, player)
        if board_before != board:
            raise ValueError(f"{player} agent mutated its input board")
        if move not in moves:
            raise ValueError(f"{player} agent returned illegal move {move}")

        board = board_after_move(board, player, move)
        if verbose:
            print(f"{player}: {move}")
            print(render_board(board), "\n")
        player = opponent_of(player)

    counts = score(board)
    if counts[BLACK] > counts[WHITE]:
        winner = BLACK
    elif counts[WHITE] > counts[BLACK]:
        winner = WHITE
    else:
        winner = "tie"
    return {"board": board, "black": counts[BLACK], "white": counts[WHITE], "winner": winner}


if __name__ == "__main__":
    result = run_game(random_ai, random_ai)
    print(render_board(result["board"]))
    print(f"Winner: {result['winner']}")
