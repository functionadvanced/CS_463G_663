ROAD = 0
DOOR = 1
WALL = 2
KEY = 3
EXIT = 4
PLAYER = 5

DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def find_tile(grid: list[list[int]], tile: int) -> tuple[int, int]:
    """Return the coordinate of the first matching tile."""
    for row, values in enumerate(grid):
        for col, value in enumerate(values):
            if value == tile:
                return row, col
    raise ValueError(f"tile {tile} is missing")


def neighbors(row: int, col: int, height: int, width: int):
    """Yield orthogonally adjacent coordinates inside the grid."""
    for d_row, d_col in DIRECTIONS:
        next_row = row + d_row
        next_col = col + d_col
        if 0 <= next_row < height and 0 <= next_col < width:
            yield next_row, next_col


class Solution:
    def shortest_path(
        self, grid: list[list[int]]
    ) -> list[tuple[int, int]] | None:
        """Return a shortest legal path, or None when none exists."""
        raise NotImplementedError("Implement Homework 1 here")
