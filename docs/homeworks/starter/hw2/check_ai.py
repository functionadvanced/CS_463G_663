from ai import (
    alpha_beta_ai,
    board_after_move,
    greedy_ai,
    legal_moves,
    minimax_ai,
    random_ai,
    utility,
)
from reversi import initial_board


def check_move_function(name, function, board, player, *extra):
    before = [row[:] for row in board]
    try:
        move = function(board, player, *extra)
    except NotImplementedError:
        print(f"{name}: TODO")
        return
    assert board == before, f"{name} mutated the input board"
    assert move in legal_moves(board, player), f"{name} returned {move}"
    print(f"{name}: interface check passed")


def main():
    board = initial_board()
    expected = {(2, 3), (3, 2), (4, 5), (5, 4)}
    assert set(legal_moves(board, "black")) == expected

    before = [row[:] for row in board]
    moved = board_after_move(board, "black", (2, 3))
    assert board == before
    assert moved[2][3] == "black" and moved[3][3] == "black"
    assert random_ai(board, "black") in expected
    print("starter helpers: passed")

    try:
        value = utility(board, "black")
    except NotImplementedError:
        print("utility: TODO")
    else:
        assert isinstance(value, (int, float))
        print("utility: interface check passed")

    check_move_function("greedy_ai", greedy_ai, board, "black")
    check_move_function("minimax_ai", minimax_ai, board, "black", 2)
    check_move_function("alpha_beta_ai", alpha_beta_ai, board, "black", 2)


if __name__ == "__main__":
    main()
