from hw1 import Solution

ROAD, DOOR, WALL, KEY, EXIT, PLAYER = range(6)


def find_tile(grid, target):
    return next(
        (row, col)
        for row, values in enumerate(grid)
        for col, tile in enumerate(values)
        if tile == target
    )


def path_is_legal(grid, path):
    if not path:
        return False

    board = [row[:] for row in grid]
    height = len(board)
    width = len(board[0])
    start = find_tile(board, PLAYER)
    goal = find_tile(board, EXIT)

    if path[0] != start:
        return False

    keys = 0
    previous = start
    for step in path[1:]:
        if not (
            isinstance(step, tuple)
            and len(step) == 2
            and all(isinstance(value, int) for value in step)
        ):
            return False

        row, col = step
        if not (0 <= row < height and 0 <= col < width):
            return False
        if abs(row - previous[0]) + abs(col - previous[1]) != 1:
            return False

        tile = board[row][col]
        if tile == WALL:
            return False
        if tile == KEY:
            keys += 1
            board[row][col] = ROAD
        elif tile == DOOR:
            if keys == 0:
                return False
            keys -= 1
            board[row][col] = ROAD

        previous = step

    return path[-1] == goal


CASES = [
    (
        [[4, 2, 1, 3], [0, 5, 0, 2], [2, 3, 1, 0]],
        3,
    ),
    (
        [
            [1, 0, 3, 2, 1],
            [2, 3, 0, 0, 1],
            [3, 0, 3, 0, 2],
            [0, 4, 1, 5, 2],
            [2, 1, 2, 3, 0],
        ],
        5,
    ),
    (
        [[5, 1, 4], [2, 2, 2], [3, 0, 0]],
        None,
    ),
]


def main():
    solution = Solution()
    for number, (grid, expected_length) in enumerate(CASES, 1):
        try:
            result = solution.shortest_path([row[:] for row in grid])
        except NotImplementedError:
            print("shortest_path: TODO")
            return
        if expected_length is None:
            assert result is None, f"case {number}: expected None"
        else:
            assert path_is_legal(grid, result), f"case {number}: illegal path"
            assert len(result) == expected_length, (
                f"case {number}: expected length {expected_length}, "
                f"received {len(result)}"
            )
        print(f"case {number}: passed")


if __name__ == "__main__":
    main()
